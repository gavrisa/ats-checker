"""
Enhanced Document Preflight System

Implements robust PDF text extraction and fragmentation detection
to block Figma-style exports while allowing legitimate CVs.
"""

import io
import logging
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available - using fallback extraction")

logger = logging.getLogger(__name__)

class PreflightTrigger(str, Enum):
    """Preflight trigger types"""
    PARSER_MALFORMED = "parser_malformed"
    ENCRYPTED_PDF = "encrypted_pdf"
    IMAGE_ONLY_NO_TEXT = "image_only_no_text"
    FIGMA_LIKE_FRAGMENTATION = "figma_like_fragmentation"
    HIGH_FRAGMENTATION_DENSITY = "high_fragmentation_density"
    LOW_TEXT_CONTENT = "low_text_content"
    PRODUCER_FIGMA_CANVA = "producer_figma_canva"
    FIGMA_GAP_PATTERN = "figma_gap_pattern"

@dataclass
class PreflightDetails:
    """Internal details for preflight results"""
    triggers: List[PreflightTrigger] = None
    total_text_chars: int = 0
    pages: int = 0
    text_pages: int = 0
    text_density: float = 0.0
    raw_metrics: Dict = None
    normalized_metrics: Dict = None
    gap_pattern_detected: bool = False
    producer_figma_canva: bool = False
    file_size: int = 0
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []
        if self.raw_metrics is None:
            self.raw_metrics = {}
        if self.normalized_metrics is None:
            self.normalized_metrics = {}

@dataclass
class PreflightResult:
    """Result of document preflight check"""
    ok: bool
    user_message: Optional[str] = None
    details: Optional[PreflightDetails] = None

# Single user-facing message (EN only, keep line breaks & bullets)
USER_MESSAGE = """Most likely this document isn't machine-readable — the bots are seeing vibes, not text.

Possible reasons:
• It's a scan (text is just an image).
• It's exported from a design tool (Figma, Canva) with outlined text.
• It's password-protected or corrupted.

Try uploading a text-based PDF, DOCX, or DOC file instead."""

# Stopwords for token analysis
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its',
    'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'i', 'you', 'we', 'they', 'this', 'these',
    'those', 'or', 'but', 'if', 'when', 'where', 'why', 'how', 'what', 'who', 'which', 'can', 'could',
    'should', 'would', 'may', 'might', 'must', 'shall', 'do', 'does', 'did', 'have', 'had', 'been',
    'being', 'am', 'are', 'is', 'was', 'were', 'be', 'being', 'been'
}

def compute_file_integrity(file_content: bytes) -> Dict[str, Union[str, int]]:
    """Compute SHA-256 hash and size for file integrity checking"""
    return {
        "hash": hashlib.sha256(file_content).hexdigest()[:16],
        "size": len(file_content)
    }

def extract_text_with_pdfplumber(file_content: bytes) -> Tuple[str, Dict]:
    """Extract text using pdfplumber with proper configuration"""
    if not PDFPLUMBER_AVAILABLE:
        return "", {"error": "pdfplumber not available"}
    
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text_parts = []
            total_chars = 0
            pages_with_text = 0
            
            for page_num, page in enumerate(pdf.pages):
                # Extract text with proper configuration
                page_text = page.extract_text(
                    x_tolerance=1,
                    y_tolerance=1,
                    layout=False,
                    x_density=7.25,
                    y_density=13,
                    keep_blank_chars=False
                )
                
                if page_text and page_text.strip():
                    text_parts.append(page_text)
                    total_chars += len(page_text)
                    pages_with_text += 1
                else:
                    text_parts.append("")
            
            full_text = " ".join(text_parts)  # Use space, not empty string
            
            return full_text, {
                "total_chars": total_chars,
                "pages": len(pdf.pages),
                "pages_with_text": pages_with_text,
                "text_density": total_chars / len(pdf.pages) if pdf.pages else 0
            }
    
    except Exception as e:
        logger.error(f"Error extracting text with pdfplumber: {e}")
        return "", {"error": str(e)}

def tokenize_text(text: str) -> Tuple[List[str], List[str]]:
    """Tokenize text into raw and normalized tokens"""
    # Split by whitespace and non-breaking spaces
    raw_tokens = re.split(r'[\s\u00A0\u2009\u200A\u200B]+', text)
    raw_tokens = [token for token in raw_tokens if token]  # Remove empty strings
    
    # Create normalized tokens (alphanumeric only, strip punctuation)
    normalized_tokens = []
    for token in raw_tokens:
        # Keep only alphanumeric characters
        normalized = re.sub(r'[^\w]', '', token)
        if normalized:
            normalized_tokens.append(normalized.lower())
    
    return raw_tokens, normalized_tokens

def compute_fragmentation_metrics(tokens: List[str], is_normalized: bool = False) -> Dict[str, float]:
    """Compute fragmentation metrics for token list"""
    if not tokens:
        return {
            "short_token_ratio": 0.0,
            "single_char_ratio": 0.0,
            "adjacent_short_seq_ratio": 0.0,
            "tokens_per_100_chars": 0.0
        }
    
    # Filter out stopwords for short token analysis
    if is_normalized:
        filtered_tokens = [t for t in tokens if t not in STOPWORDS]
    else:
        filtered_tokens = [t for t in tokens if t.lower() not in STOPWORDS]
    
    # Short token ratio (len <= 2, excluding stopwords)
    short_tokens = [t for t in filtered_tokens if len(t) <= 2]
    short_token_ratio = len(short_tokens) / len(filtered_tokens) if filtered_tokens else 0.0
    
    # Single character ratio
    single_char_tokens = [t for t in tokens if len(t) == 1]
    single_char_ratio = len(single_char_tokens) / len(tokens) if tokens else 0.0
    
    # Adjacent short sequence ratio
    adjacent_short_count = 0
    total_sequences = 0
    
    for i in range(len(tokens) - 1):
        total_sequences += 1
        if len(tokens[i]) <= 2 and len(tokens[i + 1]) <= 2:
            adjacent_short_count += 1
    
    adjacent_short_seq_ratio = adjacent_short_count / total_sequences if total_sequences else 0.0
    
    # Tokens per 100 characters (based on original text length)
    # This is computed separately as it needs the original text length
    
    return {
        "short_token_ratio": short_token_ratio,
        "single_char_ratio": single_char_ratio,
        "adjacent_short_seq_ratio": adjacent_short_seq_ratio
    }

def detect_gap_pattern(text: str) -> bool:
    """Detect gap pattern in text (simplified implementation)"""
    # This is a simplified gap detection
    # In a full implementation, you'd analyze character positions from PDF
    # For now, we'll use text density as a proxy
    
    lines = text.split('\n')
    if not lines:
        return False
    
    # Count lines with very short content (potential fragmentation)
    short_lines = 0
    for line in lines:
        if len(line.strip()) < 10:  # Very short lines might indicate fragmentation
            short_lines += 1
    
    # If more than 30% of lines are very short, consider it fragmented
    return (short_lines / len(lines)) > 0.3 if lines else False

def detect_producer_figma_canva(file_content: bytes) -> bool:
    """Detect if PDF was created by Figma/Canva"""
    try:
        # Look for Figma/Canva in PDF metadata
        content_str = file_content.decode('latin-1', errors='ignore')
        return any(keyword in content_str.lower() for keyword in ['figma', 'canva'])
    except:
        return False

def preflight_document(file_content: bytes, filename: str) -> PreflightResult:
    """Main preflight function"""
    details = PreflightDetails()
    details.file_size = len(file_content)
    
    # Extract text
    text, extraction_info = extract_text_with_pdfplumber(file_content)
    details.total_text_chars = extraction_info.get("total_chars", 0)
    details.pages = extraction_info.get("pages", 0)
    details.text_pages = extraction_info.get("pages_with_text", 0)
    details.text_density = extraction_info.get("text_density", 0.0)
    
    # Check for extraction errors
    if "error" in extraction_info:
        details.triggers.append(PreflightTrigger.PARSER_MALFORMED)
        return PreflightResult(ok=False, user_message=USER_MESSAGE, details=details)
    
    # Check for no text
    if details.total_text_chars == 0:
        details.triggers.append(PreflightTrigger.IMAGE_ONLY_NO_TEXT)
        return PreflightResult(ok=False, user_message=USER_MESSAGE, details=details)
    
    # Tokenize text
    raw_tokens, normalized_tokens = tokenize_text(text)
    
    # Compute metrics
    details.raw_metrics = compute_fragmentation_metrics(raw_tokens, is_normalized=False)
    details.normalized_metrics = compute_fragmentation_metrics(normalized_tokens, is_normalized=True)
    
    # Add tokens per 100 chars
    details.raw_metrics["tokens_per_100_chars"] = (len(raw_tokens) / details.total_text_chars) * 100 if details.total_text_chars > 0 else 0
    details.normalized_metrics["tokens_per_100_chars"] = (len(normalized_tokens) / details.total_text_chars) * 100 if details.total_text_chars > 0 else 0
    
    # Detect gap pattern
    details.gap_pattern_detected = detect_gap_pattern(text)
    
    # Detect producer
    details.producer_figma_canva = detect_producer_figma_canva(file_content)
    
    # Apply blocking rules
    
    # Rule 1: Figma-like fragmentation (2 of 3 on RAW or NORM branch)
    for metrics in [details.raw_metrics, details.normalized_metrics]:
        fragmentation_count = 0
        if metrics["short_token_ratio"] >= 0.15:  # More aggressive
            fragmentation_count += 1
        if metrics["single_char_ratio"] >= 0.08:  # More aggressive
            fragmentation_count += 1
        if metrics["adjacent_short_seq_ratio"] >= 0.05:  # More aggressive
            fragmentation_count += 1
        
        if fragmentation_count >= 2:
            details.triggers.append(PreflightTrigger.FIGMA_LIKE_FRAGMENTATION)
            break
    
    # Rule 2: High fragmentation density (very high threshold for legitimate CVs)
    for metrics in [details.raw_metrics, details.normalized_metrics]:
        if metrics["tokens_per_100_chars"] >= 50.0:  # Very high threshold for legitimate CVs
            details.triggers.append(PreflightTrigger.HIGH_FRAGMENTATION_DENSITY)
            break
    
    # Rule 3: Low text content (more lenient for legitimate CVs)
    if details.pages == 1 and details.total_text_chars < 1000:  # Much lower threshold
        details.triggers.append(PreflightTrigger.LOW_TEXT_CONTENT)
    elif details.pages >= 2 and details.text_density < 50:  # More lenient
        details.triggers.append(PreflightTrigger.LOW_TEXT_CONTENT)
    
    # Rule 4: Producer hint with relaxed thresholds (only if fragmentation is also detected)
    if details.producer_figma_canva:
        # Only trigger if there's also evidence of fragmentation
        fragmentation_evidence = False
        for metrics in [details.raw_metrics, details.normalized_metrics]:
            if (metrics["short_token_ratio"] >= 0.10 or 
                metrics["adjacent_short_seq_ratio"] >= 0.03 or 
                details.gap_pattern_detected):
                fragmentation_evidence = True
                break
        
        if fragmentation_evidence:
            details.triggers.append(PreflightTrigger.PRODUCER_FIGMA_CANVA)
    
    # Rule 5: Gap pattern
    if details.gap_pattern_detected:
        details.triggers.append(PreflightTrigger.FIGMA_GAP_PATTERN)
    
    # If any triggers found, block the document
    if details.triggers:
        return PreflightResult(ok=False, user_message=USER_MESSAGE, details=details)
    
    # All checks passed
    return PreflightResult(ok=True, details=details)
