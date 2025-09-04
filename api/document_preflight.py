"""
Document Preflight System

Fast "machine-readability" preflight check for PDF, DOCX, and DOC files.
Detects unreadable files before processing and blocks them with a friendly message.
"""

import io
import logging
import re
import zipfile
from typing import Optional, Tuple, List
import PyPDF2
from preflight_types import (
    PreflightResult, PreflightDetails, MimeType, Triggers, USER_MESSAGE,
    MAX_FILE_SIZE, MAX_PAGES, MIN_TEXT_CHARS_DOCX_DOC,
    MAX_SINGLE_CHAR_TOKENS_RATIO, MAX_SPACED_TOKENS_RATIO
)

logger = logging.getLogger(__name__)


class DocumentPreflight:
    """Main preflight system for document validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def preflight_document(self, file_content: bytes, filename: str) -> PreflightResult:
        """
        Main preflight method that runs all checks in sequence.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename for logging
            
        Returns:
            PreflightResult with ok=True to continue or ok=False to block
        """
        try:
            # Check file size
            if len(file_content) > MAX_FILE_SIZE:
                return PreflightResult(
                    ok=False,
                    user_message=USER_MESSAGE,
                    details=PreflightDetails(
                        mime=MimeType.UNKNOWN,
                        triggers=["file_too_large"]
                    )
                )
            
            # Detect MIME type by magic bytes
            mime_type = self._detect_mime_type(file_content)
            
            # Route to appropriate handler
            if mime_type == MimeType.PDF:
                return self._preflight_pdf(file_content, filename)
            elif mime_type == MimeType.DOCX:
                return self._preflight_docx(file_content, filename)
            elif mime_type == MimeType.DOC:
                return self._preflight_doc(file_content, filename)
            else:
                # Check if it's a text file
                return self._preflight_text(file_content, filename)
                
        except Exception as e:
            self.logger.error(f"Preflight error for {filename}: {e}")
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=PreflightDetails(
                    mime=MimeType.UNKNOWN,
                    triggers=["preflight_error"]
                )
            )
    
    def _detect_mime_type(self, file_content: bytes) -> MimeType:
        """Detect MIME type by magic bytes"""
        if file_content.startswith(b'%PDF'):
            return MimeType.PDF
        elif file_content.startswith(b'PK\x03\x04') and b'word/' in file_content[:1024]:
            return MimeType.DOCX
        elif file_content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return MimeType.DOC
        else:
            # Check if it's plain text
            try:
                # Try to decode as UTF-8
                text = file_content.decode('utf-8')
                # If it's mostly printable characters, treat as text
                printable_chars = sum(1 for c in text if c.isprintable() or c.isspace())
                if printable_chars / len(text) > 0.8:
                    return MimeType.UNKNOWN  # We'll handle text files specially
            except:
                pass
            return MimeType.UNKNOWN
    
    def _preflight_pdf(self, file_content: bytes, filename: str) -> PreflightResult:
        """Preflight check for PDF files with improved Figma detection"""
        from preflight_types import (
            MIN_TEXT_CHARS_PDF_SINGLE, MIN_TEXT_CHARS_PDF_MULTI,
            SHORT_TOKEN_RATIO_THRESHOLD, SINGLE_CHAR_RATIO_THRESHOLD,
            ADJACENT_SHORT_SEQ_RATIO_THRESHOLD, PRODUCER_SHORT_TOKEN_RATIO_THRESHOLD,
            PRODUCER_ADJACENT_SHORT_SEQ_THRESHOLD, GAP_PATTERN_THRESHOLD,
            DEBUG_FIGMA_DETECTION, FIGMA_SUSPICIOUS_SIZE
        )
        
        details = PreflightDetails(mime=MimeType.PDF)
        triggers = []
        
        try:
            # Use pdfplumber for better text extraction
            import pdfplumber
            
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                details.pages = len(pdf.pages)
                
                # Check page limit - TEMPORARILY DISABLED
                # if details.pages > MAX_PAGES:
                #     triggers.append("too_many_pages")
                
                # Check for suspicious file size (Figma exports are often large) - DISABLED
                # if len(file_content) > FIGMA_SUSPICIOUS_SIZE:
                #     triggers.append(Triggers.FIGMA_SUSPICIOUS_SIZE)
                
                # Extract text with proper settings
                total_text = ""
                text_pages = 0
                images_total = 0
                all_text_items = []
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Extract text using pdfplumber
                        page_text = page.extract_text()
                        
                        if page_text and page_text.strip():
                            total_text += page_text
                            text_pages += 1
                            
                            # For gap detection, we'll use a simplified approach
                            # since pdfplumber doesn't provide the same text items structure
                            # We'll create mock items for gap detection
                            words = page_text.split()
                            for i, word in enumerate(words):
                                if word.strip():
                                    all_text_items.append({
                                        'str': word,
                                        'x': i * 50,  # Mock x position
                                        'y': 0,       # Mock y position
                                        'width': len(word) * 10  # Mock width
                                    })
                        
                        # Count images
                        images = page.images
                        images_total += len(images)
                                
                    except Exception as e:
                        self.logger.warning(f"Error processing PDF page {page_num}: {e}")
                        continue
                
                # Calculate text metrics (non-whitespace chars from extracted text)
                details.total_text_chars = len([c for c in total_text if not c.isspace()])
                details.text_pages = text_pages
                details.images_total = images_total
                
                if details.pages > 0:
                    details.text_density = round(details.total_text_chars / details.pages)
                
                # Detect PDF metadata for Figma/Canva
                metadata = self._detect_pdf_metadata_improved(pdf)
                
                # Apply basic triggers
                if details.total_text_chars == 0 and details.images_total >= details.pages:
                    triggers.append(Triggers.IMAGE_ONLY_NO_TEXT)
                
                if details.total_text_chars == 0:
                    triggers.append(Triggers.OUTLINED_OR_NO_FONTS)
                
                # Calculate dual fragmentation metrics for Figma detection
                if details.total_text_chars > 0:
                    metrics_raw, metrics_norm = self._calculate_dual_fragmentation_metrics(total_text)
                    
                    # Calculate gap-based detection
                    gap_pattern = self._detect_gap_pattern(all_text_items)
                    
                    # Debug logging
                    if DEBUG_FIGMA_DETECTION:
                        self._log_debug_metrics(filename, metrics_raw, metrics_norm, gap_pattern, metadata)
                    
                    # Check Figma-like fragmentation (OR logic - any branch can trigger) - TEMPORARILY DISABLED
                    # figma_detected = False
                    
                    # # Check raw metrics
                    # if (metrics_raw['short_token_ratio'] >= SHORT_TOKEN_RATIO_THRESHOLD or
                    #     metrics_raw['single_char_ratio'] >= SINGLE_CHAR_RATIO_THRESHOLD or
                    #     metrics_raw['adjacent_short_seq_ratio'] >= ADJACENT_SHORT_SEQ_RATIO_THRESHOLD):
                    #     figma_detected = True
                    
                    # # Check normalized metrics
                    # if (metrics_norm['short_token_ratio'] >= SHORT_TOKEN_RATIO_THRESHOLD or
                    #     metrics_norm['single_char_ratio'] >= SINGLE_CHAR_RATIO_THRESHOLD or
                    #     metrics_norm['adjacent_short_seq_ratio'] >= ADJACENT_SHORT_SEQ_RATIO_THRESHOLD):
                    #     figma_detected = True
                    
                    # # Check gap pattern - TEMPORARILY DISABLED
                    # # if gap_pattern:
                    # #     triggers.append(Triggers.FIGMA_GAP_PATTERN)
                    # #     figma_detected = True
                    
                    # if figma_detected:
                    #     triggers.append(Triggers.FIGMA_LIKE_FRAGMENTATION)
                    
                    # Check producer-based detection with lower thresholds - TEMPORARILY DISABLED
                    # if metadata['producer_figma_canva']:
                    #     triggers.append(Triggers.PRODUCER_FIGMA_CANVA)
                    #     if (metrics_raw['short_token_ratio'] >= PRODUCER_SHORT_TOKEN_RATIO_THRESHOLD or
                    #         metrics_norm['short_token_ratio'] >= PRODUCER_SHORT_TOKEN_RATIO_THRESHOLD or
                    #         metrics_raw['adjacent_short_seq_ratio'] >= PRODUCER_ADJACENT_SHORT_SEQ_THRESHOLD or
                    #         metrics_norm['adjacent_short_seq_ratio'] >= PRODUCER_ADJACENT_SHORT_SEQ_THRESHOLD or
                    #         gap_pattern):
                    #         triggers.append(Triggers.FIGMA_LIKE_FRAGMENTATION)
                    
                    # Temporarily disable untagged PDF detection for legitimate CVs
                    # if metadata['untagged_pdf']:
                    #     triggers.append(Triggers.UNTAGGED_PDF)
                
                # Check low text for CVs (realistic thresholds) - TEMPORARILY DISABLED
                # if details.pages == 1 and details.total_text_chars < MIN_TEXT_CHARS_PDF_SINGLE:
                #     triggers.append(Triggers.INSUFFICIENT_TEXT)
                # elif details.pages >= 2 and details.text_density < MIN_TEXT_CHARS_PDF_MULTI:
                #     triggers.append(Triggers.INSUFFICIENT_TEXT)
                
                details.triggers = triggers
                
                # Debug logging for triggers
                if DEBUG_FIGMA_DETECTION:
                    self.logger.info(f"=== TRIGGERS DEBUG for {filename} ===")
                    self.logger.info(f"Triggers found: {triggers}")
                    self.logger.info(f"File size: {len(file_content)} bytes")
                    self.logger.info(f"FIGMA_SUSPICIOUS_SIZE: {FIGMA_SUSPICIOUS_SIZE}")
                    self.logger.info("=== END TRIGGERS DEBUG ===")
                
                # Acceptance criteria for PDFs
                if not triggers:
                    return PreflightResult(ok=True, details=details)
                
                # Block if any triggers fired
                return PreflightResult(
                    ok=False,
                    user_message=USER_MESSAGE,
                    details=details
                )
            
        except Exception as e:
            self.logger.error(f"PDF preflight error for {filename}: {e}")
            self.logger.error(f"Exception type: {type(e)}")
            self.logger.error(f"Exception details: {str(e)}")
            triggers.append(Triggers.PARSER_MALFORMED)
            details.triggers = triggers
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=details
            )
    
    def _preflight_docx(self, file_content: bytes, filename: str) -> PreflightResult:
        """Preflight check for DOCX files"""
        details = PreflightDetails(mime=MimeType.DOCX)
        triggers = []
        
        try:
            # Parse DOCX as ZIP
            with zipfile.ZipFile(io.BytesIO(file_content)) as docx_zip:
                # Extract text from document.xml
                try:
                    document_xml = docx_zip.read('word/document.xml').decode('utf-8')
                except KeyError:
                    triggers.append(Triggers.PARSER_MALFORMED_DOCX)
                    details.triggers = triggers
                    return PreflightResult(
                        ok=False,
                        user_message=USER_MESSAGE,
                        details=details
                    )
                
                # Extract text content
                text_content = self._extract_docx_text(document_xml)
                details.total_text_chars = len(re.sub(r'\s+', '', text_content))
                
                # Count images/drawings
                images_count = self._count_docx_images(document_xml)
                details.images_total = images_count
                
                # Apply triggers
                if details.total_text_chars == 0 and images_count >= 1:
                    triggers.append(Triggers.DOCX_IMAGE_ONLY)
                
                if details.total_text_chars < MIN_TEXT_CHARS_DOCX_DOC:
                    triggers.append(Triggers.DOCX_LOW_TEXT)
                
                details.triggers = triggers
                
                # Acceptance criteria
                if not triggers and details.total_text_chars >= MIN_TEXT_CHARS_DOCX_DOC:
                    return PreflightResult(ok=True, details=details)
                
                # Block if any triggers fired
                return PreflightResult(
                    ok=False,
                    user_message=USER_MESSAGE,
                    details=details
                )
                
        except Exception as e:
            self.logger.error(f"DOCX preflight error for {filename}: {e}")
            triggers.append(Triggers.PARSER_MALFORMED_DOCX)
            details.triggers = triggers
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=details
            )
    
    def _preflight_doc(self, file_content: bytes, filename: str) -> PreflightResult:
        """Preflight check for DOC files"""
        details = PreflightDetails(mime=MimeType.DOC)
        triggers = []
        
        try:
            # For DOC files, we'll use a simple approach
            # In a production system, you'd use antiword or similar
            # For now, we'll try to extract basic text patterns
            
            # Convert to string and look for readable text patterns
            try:
                # This is a simplified approach - in production use proper DOC parser
                text_content = file_content.decode('utf-8', errors='ignore')
                # Remove binary data and keep only printable characters
                text_content = re.sub(r'[^\x20-\x7E\n\r\t]', '', text_content)
                details.total_text_chars = len(re.sub(r'\s+', '', text_content))
            except:
                details.total_text_chars = 0
            
            # Apply triggers
            if details.total_text_chars < MIN_TEXT_CHARS_DOCX_DOC:
                triggers.append(Triggers.DOC_LOW_TEXT)
            
            details.triggers = triggers
            
            # Acceptance criteria
            if not triggers and details.total_text_chars >= MIN_TEXT_CHARS_DOCX_DOC:
                return PreflightResult(ok=True, details=details)
            
            # Block if any triggers fired
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"DOC preflight error for {filename}: {e}")
            triggers.append(Triggers.PARSER_MALFORMED_DOC)
            details.triggers = triggers
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=details
            )
    
    def _extract_docx_text(self, document_xml: str) -> str:
        """Extract text content from DOCX document.xml"""
        # Simple regex to extract text from <w:t> tags
        text_pattern = r'<w:t[^>]*>([^<]*)</w:t>'
        matches = re.findall(text_pattern, document_xml)
        return ' '.join(matches)
    
    def _count_docx_images(self, document_xml: str) -> int:
        """Count images/drawings in DOCX document"""
        # Count drawing and picture elements
        drawing_count = len(re.findall(r'<w:drawing', document_xml))
        pic_count = len(re.findall(r'<pic:pic', document_xml))
        return drawing_count + pic_count
    
    def _has_figma_like_spacing(self, text: str) -> bool:
        """Detect Figma-like spacing patterns"""
        if not text.strip():
            return False
        
        # Split into tokens (words)
        tokens = re.findall(r'\S+', text)
        if len(tokens) < 10:  # Need enough tokens to analyze
            return False
        
        # Check for single character tokens
        single_char_tokens = sum(1 for token in tokens if len(token) == 1)
        single_char_ratio = single_char_tokens / len(tokens)
        
        # Check for spaced-out tokens (like "S P A C E D")
        spaced_tokens = sum(1 for token in tokens if re.match(r'^[A-Z]\s+[A-Z]', token))
        spaced_ratio = spaced_tokens / len(tokens)
        
        return (single_char_ratio >= MAX_SINGLE_CHAR_TOKENS_RATIO or 
                spaced_ratio >= MAX_SPACED_TOKENS_RATIO)
    
    def _preflight_text(self, file_content: bytes, filename: str) -> PreflightResult:
        """Preflight check for text files"""
        details = PreflightDetails(mime=MimeType.UNKNOWN)
        triggers = []
        
        try:
            # Try to decode as text
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                triggers.append("invalid_encoding")
                details.triggers = triggers
                return PreflightResult(
                    ok=False,
                    user_message=USER_MESSAGE,
                    details=details
                )
            
            # Calculate text metrics
            details.total_text_chars = len(re.sub(r'\s+', '', text_content))
            
            # Apply triggers
            if details.total_text_chars < MIN_TEXT_CHARS_DOCX_DOC:
                triggers.append("insufficient_text")
            
            details.triggers = triggers
            
            # Acceptance criteria for text files
            if not triggers and details.total_text_chars >= MIN_TEXT_CHARS_DOCX_DOC:
                return PreflightResult(ok=True, details=details)
            
            # Block if any triggers fired
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Text preflight error for {filename}: {e}")
            triggers.append("preflight_error")
            details.triggers = triggers
            return PreflightResult(
                ok=False,
                user_message=USER_MESSAGE,
                details=details
            )
    
    def _tokenize_text(self, text: str) -> tuple[list[str], list[str]]:
        """Tokenize text and return (all_tokens, alnum_tokens)"""
        # Split into tokens, normalize whitespace
        tokens = re.findall(r'\S+', text.lower())
        
        # Create alnum_tokens: strip non-alphanumeric, filter empty
        alnum_tokens = []
        for token in tokens:
            # Strip punctuation around tokens
            clean_token = re.sub(r'^[^\w]+|[^\w]+$', '', token)
            if len(clean_token) > 0:
                alnum_tokens.append(clean_token)
        
        return tokens, alnum_tokens
    
    def _calculate_fragmentation_metrics(self, text: str) -> dict:
        """Calculate fragmentation metrics for Figma detection"""
        from preflight_types import (
            STOPWORDS, SHORT_TOKEN_RATIO_THRESHOLD, SINGLE_CHAR_RATIO_THRESHOLD,
            ADJACENT_SHORT_SEQ_RATIO_THRESHOLD, TOKENS_PER_100_CHARS_THRESHOLD
        )
        
        tokens, alnum_tokens = self._tokenize_text(text)
        
        if not alnum_tokens:
            return {
                'short_token_ratio': 1.0,
                'single_char_ratio': 1.0,
                'adjacent_short_seq_ratio': 1.0,
                'tokens_per_100_chars': 0.0
            }
        
        # Calculate short_token_ratio (excluding stopwords)
        non_stopword_tokens = [t for t in alnum_tokens if t not in STOPWORDS]
        short_tokens = [t for t in non_stopword_tokens if len(t) <= 2]
        short_token_ratio = len(short_tokens) / max(len(non_stopword_tokens), 1)
        
        # Calculate single_char_ratio
        single_char_tokens = [t for t in alnum_tokens if len(t) == 1]
        single_char_ratio = len(single_char_tokens) / max(len(alnum_tokens), 1)
        
        # Calculate adjacent_short_seq_ratio (consecutive short tokens)
        adjacent_short_count = 0
        total_bigrams = 0
        
        for i in range(len(alnum_tokens) - 1):
            total_bigrams += 1
            if len(alnum_tokens[i]) <= 2 and len(alnum_tokens[i + 1]) <= 2:
                adjacent_short_count += 1
        
        # Also check trigrams
        for i in range(len(alnum_tokens) - 2):
            total_bigrams += 1
            if (len(alnum_tokens[i]) <= 2 and 
                len(alnum_tokens[i + 1]) <= 2 and 
                len(alnum_tokens[i + 2]) <= 2):
                adjacent_short_count += 1
        
        adjacent_short_seq_ratio = adjacent_short_count / max(total_bigrams, 1)
        
        # Calculate tokens_per_100_chars
        total_text_chars = len([c for c in text if not c.isspace()])
        tokens_per_100_chars = (len(alnum_tokens) / max(total_text_chars, 1)) * 100
        
        return {
            'short_token_ratio': short_token_ratio,
            'single_char_ratio': single_char_ratio,
            'adjacent_short_seq_ratio': adjacent_short_seq_ratio,
            'tokens_per_100_chars': tokens_per_100_chars,
            'total_text_chars': total_text_chars,
            'alnum_tokens_count': len(alnum_tokens)
        }
    
    def _detect_pdf_metadata_improved(self, pdf) -> dict:
        """Detect PDF metadata for Figma/Canva detection using pdfplumber"""
        metadata = {
            'producer_figma_canva': False,
            'untagged_pdf': False
        }
        
        try:
            # Check Producer/Creator metadata
            if hasattr(pdf, 'metadata') and pdf.metadata:
                producer = str(pdf.metadata.get('Producer', '')).lower()
                creator = str(pdf.metadata.get('Creator', '')).lower()
                
                if 'figma' in producer or 'figma' in creator or 'canva' in producer or 'canva' in creator:
                    metadata['producer_figma_canva'] = True
            
            # Check for StructTreeRoot (tagged PDF) - simplified check
            # pdfplumber doesn't expose this easily, so we'll assume untagged for now
            metadata['untagged_pdf'] = True
                    
        except Exception as e:
            self.logger.warning(f"Error detecting PDF metadata: {e}")
        
        return metadata
    
    def _calculate_dual_fragmentation_metrics(self, text: str) -> tuple[dict, dict]:
        """Calculate both raw and normalized fragmentation metrics"""
        # Raw metrics - tokenize with whitespace preservation
        tokens_raw = re.split(r'[\s\u00A0\u2009\u200A\u200B]+', text)
        tokens_raw = [t for t in tokens_raw if t]  # Remove empty tokens
        
        # Normalized metrics - apply normalization but preserve inter-token spaces
        text_norm = text.lower()
        # Apply NFKC normalization and strip punctuation around tokens
        import unicodedata
        text_norm = unicodedata.normalize('NFKC', text_norm)
        tokens_norm = re.split(r'[\s\u00A0\u2009\u200A\u200B]+', text_norm)
        tokens_norm = [re.sub(r'^[^\w]+|[^\w]+$', '', t) for t in tokens_norm if t]
        tokens_norm = [t for t in tokens_norm if t]  # Remove empty tokens
        
        # Calculate metrics for both
        metrics_raw = self._calculate_metrics_for_tokens(tokens_raw, text)
        metrics_norm = self._calculate_metrics_for_tokens(tokens_norm, text)
        
        return metrics_raw, metrics_norm
    
    def _calculate_metrics_for_tokens(self, tokens: list[str], original_text: str) -> dict:
        """Calculate fragmentation metrics for a token list"""
        from preflight_types import STOPWORDS
        
        if not tokens:
            return {
                'short_token_ratio': 1.0,
                'single_char_ratio': 1.0,
                'adjacent_short_seq_ratio': 1.0
            }
        
        # Calculate short_token_ratio (excluding stopwords)
        non_stopword_tokens = [t for t in tokens if t not in STOPWORDS]
        short_tokens = [t for t in non_stopword_tokens if len(t) <= 2]
        short_token_ratio = len(short_tokens) / max(len(non_stopword_tokens), 1)
        
        # Calculate single_char_ratio
        single_char_tokens = [t for t in tokens if len(t) == 1]
        single_char_ratio = len(single_char_tokens) / max(len(tokens), 1)
        
        # Calculate adjacent_short_seq_ratio (consecutive short tokens)
        adjacent_short_count = 0
        total_bigrams = 0
        
        for i in range(len(tokens) - 1):
            total_bigrams += 1
            if len(tokens[i]) <= 2 and len(tokens[i + 1]) <= 2:
                adjacent_short_count += 1
        
        # Also check trigrams
        for i in range(len(tokens) - 2):
            total_bigrams += 1
            if (len(tokens[i]) <= 2 and 
                len(tokens[i + 1]) <= 2 and 
                len(tokens[i + 2]) <= 2):
                adjacent_short_count += 1
        
        adjacent_short_seq_ratio = adjacent_short_count / max(total_bigrams, 1)
        
        return {
            'short_token_ratio': short_token_ratio,
            'single_char_ratio': single_char_ratio,
            'adjacent_short_seq_ratio': adjacent_short_seq_ratio
        }
    
    def _detect_gap_pattern(self, text_items: list) -> bool:
        """Detect Figma gap pattern based on character spacing"""
        from preflight_types import GAP_PATTERN_THRESHOLD
        
        if not text_items:
            return False
        
        try:
            # Sort items by y position (top to bottom), then by x position (left to right)
            sorted_items = sorted(text_items, key=lambda item: (item.get('y', 0), item.get('x', 0)))
            
            gaps = []
            char_widths = []
            
            for i, item in enumerate(sorted_items):
                if not item.get('str') or len(item['str']) == 0:
                    continue
                
                # Calculate character width
                width = item.get('width', 0)
                char_count = len(item['str'])
                if char_count > 0:
                    char_width = width / char_count
                    char_widths.append(char_width)
                
                # Calculate gap to next item
                if i < len(sorted_items) - 1:
                    next_item = sorted_items[i + 1]
                    if next_item.get('str'):
                        gap = next_item.get('x', 0) - (item.get('x', 0) + item.get('width', 0))
                        if gap > 0:
                            gaps.append(gap)
            
            if not gaps or not char_widths:
                return False
            
            # Calculate median character width
            char_widths.sort()
            median_char_width = char_widths[len(char_widths) // 2]
            
            # Count gaps that are significantly larger than median character width
            large_gaps = [gap for gap in gaps if gap > median_char_width * 0.6]
            gap_ratio = len(large_gaps) / len(gaps)
            
            return gap_ratio >= GAP_PATTERN_THRESHOLD
            
        except Exception as e:
            self.logger.warning(f"Error detecting gap pattern: {e}")
            return False
    
    def _log_debug_metrics(self, filename: str, metrics_raw: dict, metrics_norm: dict, 
                          gap_pattern: bool, metadata: dict):
        """Log debug metrics for Figma detection"""
        self.logger.info(f"=== FIGMA DETECTION DEBUG for {filename} ===")
        self.logger.info(f"Raw metrics: {metrics_raw}")
        self.logger.info(f"Normalized metrics: {metrics_norm}")
        self.logger.info(f"Gap pattern detected: {gap_pattern}")
        self.logger.info(f"Metadata: {metadata}")
        self.logger.info("=== END DEBUG ===")


# Global preflight instance
document_preflight = DocumentPreflight()


def preflight_document(file_content: bytes, filename: str) -> PreflightResult:
    """
    Public API function for document preflight.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        PreflightResult with ok=True to continue or ok=False to block
    """
    return document_preflight.preflight_document(file_content, filename)
