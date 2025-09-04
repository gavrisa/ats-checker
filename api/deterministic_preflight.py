"""
Enhanced preflight system with deterministic locks for Figma-fragmented PDFs
"""
import hashlib
import logging
import io
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from deterministic_locks import deterministic_locks

logger = logging.getLogger(__name__)

# User-friendly error message
USER_MESSAGE = (
    "This file appears to be unreadable by automated systems. "
    "Please use a standard PDF or Word document format."
)

@dataclass
class PreflightResult:
    """Result of preflight check"""
    ok: bool
    user_message: str
    details: Optional['PreflightDetails'] = None

@dataclass
class PreflightDetails:
    """Detailed preflight information"""
    mime: str
    pages: int
    total_text_chars: int
    text_pages: int
    text_density: float
    images_total: int
    encrypted: bool
    triggers: List[str]
    # Additional metrics for deterministic locks
    dict_hits_ratio: float = 0.0
    nll_per_char: float = 0.0
    tokens_per_100_chars: float = 0.0
    short_token_ratio: float = 0.0
    adjacent_short_seq_ratio: float = 0.0
    gap_share: float = 0.0
    producer: str = ""
    has_struct_tree: bool = False

def compute_file_integrity(file_content: bytes) -> Dict[str, any]:
    """Compute file integrity hash and size"""
    return {
        'hash': hashlib.sha256(file_content).hexdigest(),
        'size': len(file_content)
    }

def compute_fragmentation_metrics(text: str) -> Dict[str, float]:
    """Compute fragmentation metrics on raw text (no healing)"""
    if not text.strip():
        return {
            'short_token_ratio': 0.0,
            'adjacent_short_seq_ratio': 0.0,
            'tokens_per_100_chars': 0.0
        }
    
    # Split into tokens (preserve raw spacing)
    tokens = text.split()
    alnum_tokens = [t for t in tokens if t.isalnum()]
    
    if not alnum_tokens:
        return {
            'short_token_ratio': 1.0,
            'adjacent_short_seq_ratio': 1.0,
            'tokens_per_100_chars': 0.0
        }
    
    # Calculate short token ratio (tokens <= 2 chars, excluding stopwords)
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    short_tokens = [t for t in alnum_tokens if len(t) <= 2 and t.lower() not in stopwords]
    short_token_ratio = len(short_tokens) / len(alnum_tokens) if alnum_tokens else 0
    
    # Calculate adjacent short sequence ratio
    adjacent_short_count = 0
    total_bigrams = 0
    
    for i in range(len(alnum_tokens) - 1):
        if len(alnum_tokens[i]) <= 2 and len(alnum_tokens[i + 1]) <= 2:
            adjacent_short_count += 1
        total_bigrams += 1
    
    adjacent_short_seq_ratio = adjacent_short_count / total_bigrams if total_bigrams > 0 else 0
    
    # Calculate tokens per 100 characters
    total_text_chars = len([c for c in text if not c.isspace()])
    tokens_per_100_chars = (len(alnum_tokens) / max(total_text_chars, 1)) * 100
    
    return {
        'short_token_ratio': short_token_ratio,
        'adjacent_short_seq_ratio': adjacent_short_seq_ratio,
        'tokens_per_100_chars': tokens_per_100_chars
    }

def extract_text_raw_pdf(file_content: bytes) -> Tuple[str, Dict]:
    """
    Extract text from PDF using raw approach with no whitespace healing
    Returns (text, metadata)
    """
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 not available")
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
        # Get page count safely
        try:
            page_count = len(pdf_reader.pages)
        except Exception as e:
            logger.warning(f"Error getting page count: {e}")
            page_count = 0
        
        # Extract basic metadata
        metadata = {
            'pages': page_count,
            'producer': '',
            'creator': '',
            'has_struct_tree': False,
            'has_mark_info': False,
            'encrypted': False  # Simplified - assume not encrypted for now
        }
        
        # Extract text using raw method - NO WHITESPACE HEALING
        text_parts = []
        text_pages = 0
        
        try:
            for i, page in enumerate(pdf_reader.pages):
                try:
                    # Use raw text extraction without any normalization
                    # This preserves the original spacing and fragmentation
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 10:
                        # DO NOT normalize whitespace - keep raw text
                        text_parts.append(page_text)
                        text_pages += 1
                        
                        # Debug logging for whitespace visibility
                        if os.getenv('PREFLIGHT_DEBUG', '0') == '1':
                            visible_text = (page_text[:200]
                                          .replace(' ', '·')
                                          .replace('\u00A0', '⍽')
                                          .replace('\u2009', ' ')
                                          .replace('\u200A', ' ')
                                          .replace('\u200B', '⎵')
                                          .replace('\n', '¶'))
                            logger.info(f"RAW_TEXT_PAGE_{i}: {visible_text}")
                            tokens = page_text.split()
                            token_info = [f"{t}|{len(t)}" for t in tokens[:10]]
                            logger.info(f"RAW_TOKENS_PAGE_{i}: {token_info}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {i}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error iterating pages: {e}")
            # Try to get at least some text
            try:
                if page_count > 0:
                    first_page = pdf_reader.pages[0]
                    page_text = first_page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        text_pages = 1
            except Exception as e2:
                logger.warning(f"Error extracting from first page: {e2}")
        
        # Join with single spaces only (no other healing)
        full_text = ' '.join(text_parts)
        
        metadata['text_pages'] = text_pages
        metadata['total_text_chars'] = len(full_text)
        metadata['text_density'] = len(full_text) / metadata['pages'] if metadata['pages'] > 0 else 0
        
        return full_text, metadata
        
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise

def calculate_fragmentation_metrics(text: str) -> Dict[str, float]:
    """Calculate fragmentation metrics on raw text"""
    if not text.strip():
        return {
            'tokens_per_100_chars': 0.0,
            'short_token_ratio': 0.0,
            'adjacent_short_seq_ratio': 0.0,
            'gap_share': 0.0
        }
    
    # Tokenize by whitespace (no other normalization)
    tokens = re.findall(r'\S+', text)
    alnum_tokens = [t for t in tokens if re.search(r'[a-zA-Z0-9]', t)]
    
    # Calculate tokens per 100 chars
    non_whitespace_chars = len(re.sub(r'\s', '', text))
    tokens_per_100_chars = (len(alnum_tokens) / non_whitespace_chars * 100) if non_whitespace_chars > 0 else 0
    
    # Calculate short token ratio (tokens <= 2 chars, excluding stopwords)
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    short_tokens = [t for t in alnum_tokens if len(t) <= 2 and t.lower() not in stopwords]
    short_token_ratio = len(short_tokens) / len(alnum_tokens) if alnum_tokens else 0
    
    # Calculate adjacent short sequence ratio
    adjacent_short_count = 0
    total_bigrams = 0
    
    for i in range(len(alnum_tokens) - 1):
        if len(alnum_tokens[i]) <= 2 and len(alnum_tokens[i+1]) <= 2:
            adjacent_short_count += 1
        total_bigrams += 1
    
    adjacent_short_seq_ratio = adjacent_short_count / total_bigrams if total_bigrams > 0 else 0
    
    # Simplified gap detection (placeholder - would need actual PDF layout analysis)
    gap_share = 0.0  # Would calculate from PDF layout data
    
    return {
        'tokens_per_100_chars': tokens_per_100_chars,
        'short_token_ratio': short_token_ratio,
        'adjacent_short_seq_ratio': adjacent_short_seq_ratio,
        'gap_share': gap_share
    }

def preflight_document(file_content: bytes, filename: str) -> PreflightResult:
    """
    Simplified preflight check with hash kill-switch
    """
    triggers = []
    
    try:
        logger.info(f"Preflight check for {filename}")
        
        # Basic file validation
        if not file_content:
            logger.info("Preflight: No file content")
            return PreflightResult(ok=False, user_message=USER_MESSAGE)
        
        # Check file type
        if not filename.lower().endswith('.pdf'):
            logger.info("Preflight: Not a PDF file")
            return PreflightResult(ok=False, user_message=USER_MESSAGE)
        
        # Hash kill-switch check (primary deterministic lock)
        hash_trigger = deterministic_locks.check_hash_killswitch(file_content)
        if hash_trigger:
            logger.info(f"Preflight: Hash kill-switch triggered: {hash_trigger}")
            triggers.append(hash_trigger)
            return PreflightResult(ok=False, user_message=USER_MESSAGE)
        
        # Extract text for deterministic locks using RAW extraction
        try:
            # Use raw text extraction (no whitespace healing)
            text, extraction_info = extract_text_raw_pdf(file_content)
            
            if not text or len(text.strip()) < 50:
                logger.info("Preflight: Insufficient text content")
                return PreflightResult(ok=False, user_message=USER_MESSAGE)
            
            # Log whitespace debug if enabled
            if os.getenv('PREFLIGHT_DEBUG', '0') == '1':
                visible_text = (text[:200]
                              .replace(' ', '·')
                              .replace('\u00A0', '⍽')
                              .replace('\u2009', ' ')
                              .replace('\u200A', ' ')
                              .replace('\u200B', '⎵')
                              .replace('\n', '¶'))
                logger.info(f"PREFLIGHT_RAW_TEXT: {visible_text}")
                tokens = text.split()
                token_info = [f"{t}|{len(t)}" for t in tokens[:10]]
                logger.info(f"PREFLIGHT_RAW_TOKENS: {token_info}")
            
            # Apply deterministic locks
            total_chars = len(text)
            
            # Compute fragmentation metrics on RAW text
            fragmentation_metrics = compute_fragmentation_metrics(text)
            short_token_ratio = fragmentation_metrics['short_token_ratio']
            adjacent_short_seq_ratio = fragmentation_metrics['adjacent_short_seq_ratio']
            tokens_per_100_chars = fragmentation_metrics['tokens_per_100_chars']
            
            # Check Figma fragmentation (2 of 3 triggers)
            fragmentation_count = 0
            if short_token_ratio >= 0.25:
                fragmentation_count += 1
                logger.info(f"Fragmentation trigger: short_token_ratio={short_token_ratio:.3f} >= 0.25")
            if adjacent_short_seq_ratio >= 0.08:
                fragmentation_count += 1
                logger.info(f"Fragmentation trigger: adjacent_short_seq_ratio={adjacent_short_seq_ratio:.3f} >= 0.08")
            if tokens_per_100_chars >= 15.0:
                fragmentation_count += 1
                logger.info(f"Fragmentation trigger: tokens_per_100_chars={tokens_per_100_chars:.1f} >= 15.0")
            
            if fragmentation_count >= 2:
                logger.info(f"Preflight: Figma fragmentation detected ({fragmentation_count}/3 triggers)")
                triggers.append("figma_fragmentation")
                return PreflightResult(ok=False, user_message=USER_MESSAGE)
            
            # Dictionary coverage lock (secondary check)
            dict_block, dict_hits = deterministic_locks.check_dictionary_coverage(text, total_chars)
            if dict_block:
                logger.info(f"Preflight: Dictionary coverage lock triggered: {dict_hits:.3f}")
                return PreflightResult(ok=False, user_message=USER_MESSAGE)
            
            # Bigram perplexity lock
            bigram_block, nll_per_char = deterministic_locks.check_bigram_perplexity(text, total_chars)
            if bigram_block:
                logger.info(f"Preflight: Bigram perplexity lock triggered: {nll_per_char:.3f}")
                return PreflightResult(ok=False, user_message=USER_MESSAGE)
            
            # Producer tagging lock (simplified - no metadata for now)
            # TODO: Add proper PDF metadata extraction
            
            logger.info("Preflight: All deterministic locks passed, allowing through")
            return PreflightResult(ok=True, user_message="")
            
        except Exception as e:
            logger.error(f"Preflight: Error in deterministic locks: {e}")
            return PreflightResult(ok=False, user_message=USER_MESSAGE)
        
    except Exception as e:
        logger.error(f"Preflight error: {e}")
        return PreflightResult(ok=False, user_message=USER_MESSAGE)

def extract_text_with_preflight(file_content: bytes, filename: str, content_type: str) -> Tuple[str, Dict]:
    """
    Extract text using preflight system
    """
    try:
        # Run preflight check
        preflight_result = preflight_document(file_content, filename)
        
        if not preflight_result.ok:
            return "", {
                "filename": filename,
                "content_type": content_type,
                "size": len(file_content),
                "ats_compatible": False,
                "text_extractable": False,
                "file_type": "pdf",
                "extraction_method": "preflight_blocked",
                "error": preflight_result.user_message,
                "preflight_details": preflight_result.details.__dict__ if preflight_result.details else None
            }
        
        # Use the existing working PDF extraction from main.py
        # Import the function from main.py
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from main import extract_text_from_file
        
        # Extract text using the working function
        text, file_info = extract_text_from_file(file_content, filename, content_type)
        
        return text, file_info
        
    except Exception as e:
        logger.error(f"Preflight text extraction error: {e}")
        return "", {
            "filename": filename,
            "content_type": content_type,
            "size": len(file_content),
            "ats_compatible": False,
            "text_extractable": False,
            "file_type": "pdf",
            "extraction_method": "preflight_error",
            "error": f"Error during preflight processing: {str(e)}"
        }
