"""
PDF Validation Module for ATS Resume Checker

Detects broken, encrypted, or image-only PDFs and provides clear error messages.
Implements comprehensive validation rules as specified in requirements.
"""

import io
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import PyPDF2
    PDF_LIBRARY_AVAILABLE = True
except ImportError:
    PDF_LIBRARY_AVAILABLE = False
    logging.warning("PyPDF2 not available - PDF validation will be limited")

logger = logging.getLogger(__name__)

class PDFErrorType(Enum):
    """PDF error types for different validation failures"""
    CORRUPT = "ERR_PDF_CORRUPT"
    ENCRYPTED = "ERR_PDF_ENCRYPTED"
    IMAGE_ONLY = "ERR_PDF_IMAGE_ONLY"
    NO_TEXT = "ERR_PDF_NO_TEXT"
    UNKNOWN = "ERR_PDF_UNKNOWN"

@dataclass
class PDFValidationResult:
    """Result of PDF validation"""
    is_valid: bool
    error_type: Optional[PDFErrorType] = None
    error_message: Optional[str] = None
    extracted_text: str = ""
    page_count: int = 0
    text_density_per_page: List[float] = None
    image_ratio_per_page: List[float] = None
    glyph_count_per_page: List[int] = None
    vector_path_count_per_page: List[int] = None
    validation_details: Dict = None

class PDFValidator:
    """
    Comprehensive PDF validator that detects:
    1. Corruption/structure errors (hard fail)
    2. Encryption/password protection (hard fail)
    3. No extractable text (hard fail)
    4. Image-only or outlined text (heuristic-based soft fail)
    """
    
    def __init__(self):
        # EXTREMELY strict parameters to match Glassdoor's rejection behavior exactly
        self.min_text_density = 0.5  # characters per square cm (very lenient threshold)
        self.good_text_density = 1.0  # characters per square cm for mixed docs (very lenient)
        self.min_glyph_count = 20  # minimum distinct glyphs per page (very lenient)
        self.image_ratio_threshold = 0.5  # ratio of image to text content (lenient)
        self.mixed_doc_threshold = 0.1  # 10% of pages need good text density (very lenient)
        
    def validate_pdf(self, file_content: bytes, filename: str = "document.pdf") -> PDFValidationResult:
        """
        Main validation method that runs all checks in sequence.
        
        Args:
            file_content: Raw PDF file bytes
            filename: Original filename for logging
            
        Returns:
            PDFValidationResult with validation status and details
        """
        logger.info(f"Starting PDF validation for {filename} ({len(file_content)} bytes)")
        
        if not PDF_LIBRARY_AVAILABLE:
            return PDFValidationResult(
                is_valid=False,
                error_type=PDFErrorType.UNKNOWN,
                error_message="PDF processing library not available"
            )
        
        try:
            # Step 1: Basic structure validation (hard fail)
            pdf_reader = self._validate_pdf_structure(file_content)
            if not pdf_reader:
                return PDFValidationResult(
                    is_valid=False,
                    error_type=PDFErrorType.CORRUPT,
                    error_message="PDF file is corrupted or has invalid structure"
                )
            
            # Step 2: Check for encryption (hard fail)
            if pdf_reader.is_encrypted:
                return PDFValidationResult(
                    is_valid=False,
                    error_type=PDFErrorType.ENCRYPTED,
                    error_message="PDF is password-protected or encrypted"
                )
            
            # Step 3: Extract text and analyze (hard fail for no text)
            text_analysis = self._analyze_text_content(pdf_reader)
            if not text_analysis["has_text"]:
                return PDFValidationResult(
                    is_valid=False,
                    error_type=PDFErrorType.NO_TEXT,
                    error_message="No extractable text found in PDF"
                )
            
            # Step 4: Heuristic analysis for image-only detection (soft fail)
            heuristic_result = self._analyze_heuristics(pdf_reader, text_analysis)
            
            # Step 5: Final validation decision
            if heuristic_result["is_image_only"]:
                return PDFValidationResult(
                    is_valid=False,
                    error_type=PDFErrorType.IMAGE_ONLY,
                    error_message="PDF appears to be image-only or contains outlined text",
                    extracted_text=text_analysis["extracted_text"],
                    page_count=text_analysis["page_count"],
                    text_density_per_page=text_analysis["text_density_per_page"],
                    image_ratio_per_page=heuristic_result["image_ratio_per_page"],
                    glyph_count_per_page=heuristic_result["glyph_count_per_page"],
                    vector_path_count_per_page=heuristic_result["vector_path_count_per_page"],
                    validation_details=heuristic_result["details"]
                )
            
            # PDF is valid
            return PDFValidationResult(
                is_valid=True,
                extracted_text=text_analysis["extracted_text"],
                page_count=text_analysis["page_count"],
                text_density_per_page=text_analysis["text_density_per_page"],
                image_ratio_per_page=heuristic_result["image_ratio_per_page"],
                glyph_count_per_page=heuristic_result["glyph_count_per_page"],
                vector_path_count_per_page=heuristic_result["vector_path_count_per_page"],
                validation_details=heuristic_result["details"]
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during PDF validation: {str(e)}")
            return PDFValidationResult(
                is_valid=False,
                error_type=PDFErrorType.UNKNOWN,
                error_message=f"Unexpected error during PDF processing: {str(e)}"
            )
    
    def _validate_pdf_structure(self, file_content: bytes) -> Optional[PyPDF2.PdfReader]:
        """
        Validate PDF structure and return PdfReader if valid.
        
        Returns:
            PyPDF2.PdfReader if valid, None if corrupted
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            
            # Check basic structure
            if len(pdf_reader.pages) == 0:
                logger.warning("PDF has zero pages")
                return None
                
            # Try to access first page to test structure
            first_page = pdf_reader.pages[0]
            _ = first_page.extract_text()  # This will fail if structure is broken
            
            logger.info(f"PDF structure validation passed - {len(pdf_reader.pages)} pages")
            return pdf_reader
            
        except Exception as e:
            logger.warning(f"PDF structure validation failed: {str(e)}")
            return None
    
    def _analyze_text_content(self, pdf_reader: PyPDF2.PdfReader) -> Dict:
        """
        Analyze text content across all pages.
        
        Returns:
            Dict with text analysis results
        """
        extracted_text = ""
        text_density_per_page = []
        page_count = len(pdf_reader.pages)
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
                
                # Calculate text density (rough approximation)
                # Assume average page size is A4 (21cm x 29.7cm = 623.7 cm²)
                page_area_cm2 = 623.7
                text_density = len(page_text.strip()) / page_area_cm2 if page_text else 0
                text_density_per_page.append(text_density)
                
                logger.debug(f"Page {page_num + 1}: {len(page_text)} chars, density: {text_density:.3f} chars/cm²")
                
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                text_density_per_page.append(0)
        
        has_text = len(extracted_text.strip()) > 0
        
        return {
            "extracted_text": extracted_text.strip(),
            "has_text": has_text,
            "page_count": page_count,
            "text_density_per_page": text_density_per_page,
            "total_text_length": len(extracted_text.strip())
        }
    
    def _analyze_heuristics(self, pdf_reader: PyPDF2.PdfReader, text_analysis: Dict) -> Dict:
        """
        Apply heuristic rules to detect image-only or outlined text PDFs.
        
        Returns:
            Dict with heuristic analysis results
        """
        page_count = text_analysis["page_count"]
        text_density_per_page = text_analysis["text_density_per_page"]
        
        # Initialize heuristic counters
        low_density_pages = 0
        low_glyph_pages = 0
        high_image_ratio_pages = 0
        high_vector_pages = 0
        
        image_ratio_per_page = []
        glyph_count_per_page = []
        vector_path_count_per_page = []
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                # Heuristic 1: Text density check
                text_density = text_density_per_page[page_num]
                if text_density < self.min_text_density:
                    low_density_pages += 1
                
                # Heuristic 2: Distinct glyph count
                page_text = page.extract_text() or ""
                unique_chars = len(set(page_text.replace(" ", "").replace("\n", "")))
                glyph_count_per_page.append(unique_chars)
                if unique_chars < self.min_glyph_count:
                    low_glyph_pages += 1
                
                # Heuristic 3: Image vs text ratio (simplified)
                # This is a rough approximation - in a real implementation,
                # you'd need to parse the PDF structure more deeply
                image_ratio = self._estimate_image_ratio(page, page_text)
                image_ratio_per_page.append(image_ratio)
                if image_ratio > self.image_ratio_threshold:
                    high_image_ratio_pages += 1
                
                # Heuristic 4: Vector paths vs text (simplified)
                # This would require deeper PDF parsing in a real implementation
                vector_path_count = self._estimate_vector_paths(page)
                vector_path_count_per_page.append(vector_path_count)
                if vector_path_count > 100 and len(page_text.strip()) < 50:
                    high_vector_pages += 1
                
            except Exception as e:
                logger.warning(f"Error analyzing page {page_num + 1} heuristics: {str(e)}")
                image_ratio_per_page.append(0)
                glyph_count_per_page.append(0)
                vector_path_count_per_page.append(0)
        
        # Calculate percentages
        low_density_percentage = low_density_pages / page_count
        low_glyph_percentage = low_glyph_pages / page_count
        high_image_ratio_percentage = high_image_ratio_pages / page_count
        high_vector_percentage = high_vector_pages / page_count
        
        # Check for mixed document (good text density on some pages)
        good_density_pages = sum(1 for density in text_density_per_page if density >= self.good_text_density)
        good_density_percentage = good_density_pages / page_count
        
        # Decision logic: image-only if heuristics fail OR not a good mixed document
        # Made more lenient to allow legitimate CVs to pass
        heuristic_failures = 0
        if low_density_percentage >= 0.8:  # Very lenient threshold (80% of pages can have low density)
            heuristic_failures += 1
        if low_glyph_percentage >= 0.8:  # Very lenient threshold (80% of pages can have low glyphs)
            heuristic_failures += 1
        if high_image_ratio_percentage >= 0.8:  # Very lenient threshold (80% of pages can be image-heavy)
            heuristic_failures += 1
        if high_vector_percentage >= 0.8:  # Very lenient threshold (80% of pages can be vector-heavy)
            heuristic_failures += 1
        
        # Flag as image-only if heuristics fail OR not a good mixed document
        # Made more lenient to allow legitimate CVs to pass
        is_image_only = (heuristic_failures >= 3 or good_density_percentage < self.mixed_doc_threshold)
        
        details = {
            "low_density_percentage": low_density_percentage,
            "low_glyph_percentage": low_glyph_percentage,
            "high_image_ratio_percentage": high_image_ratio_percentage,
            "high_vector_percentage": high_vector_percentage,
            "good_density_percentage": good_density_percentage,
            "heuristic_failures": heuristic_failures,
            "is_mixed_document": good_density_percentage >= self.mixed_doc_threshold
        }
        
        logger.info(f"Heuristic analysis: {heuristic_failures} failures, mixed doc: {good_density_percentage:.1%}")
        
        return {
            "is_image_only": is_image_only,
            "image_ratio_per_page": image_ratio_per_page,
            "glyph_count_per_page": glyph_count_per_page,
            "vector_path_count_per_page": vector_path_count_per_page,
            "details": details
        }
    
    def _estimate_image_ratio(self, page, page_text: str) -> float:
        """
        Estimate the ratio of image content to text content on a page.
        This is a simplified implementation - a real version would parse PDF objects.
        """
        try:
            # More aggressive heuristic to catch Figma exports and image-only PDFs
            text_length = len(page_text.strip())
            unique_chars = len(set(page_text.replace(" ", "").replace("\n", "")))
            
            # If very little text or very few unique characters, it's likely image-heavy
            if text_length < 100 or unique_chars < 20:
                return 0.95  # Very high image ratio (likely Figma export)
            elif text_length < 300 or unique_chars < 50:
                return 0.8   # High image ratio
            elif text_length < 500:
                return 0.6   # Medium-high image ratio
            else:
                return 0.2   # Low image ratio (good text content)
        except:
            return 0.8  # Default to high image ratio (be more conservative)
    
    def _estimate_vector_paths(self, page) -> int:
        """
        Estimate the number of vector paths on a page.
        This is a simplified implementation - a real version would parse PDF drawing commands.
        """
        try:
            # More aggressive heuristic to detect Figma exports and outlined text
            page_text = page.extract_text() or ""
            text_length = len(page_text.strip())
            unique_chars = len(set(page_text.replace(" ", "").replace("\n", "")))
            
            # If page has very little text or very few unique characters,
            # it's likely a Figma export with outlined text (high vector count)
            if text_length < 100 or unique_chars < 20:
                return 200  # Very high vector count (likely Figma export)
            elif text_length < 300 or unique_chars < 50:
                return 100  # High vector count
            else:
                return 20   # Low vector count (normal text-based PDF)
        except:
            return 100  # Default to high vector count (be more conservative)

def get_pdf_error_message(error_type: PDFErrorType) -> Dict[str, str]:
    """
    Get user-friendly error messages for different PDF error types.
    
    Returns:
        Dict with title and body messages
    """
    error_messages = {
        PDFErrorType.CORRUPT: {
            "title": "Corrupted PDF",
            "body": "This PDF file appears to be corrupted or damaged. Please try uploading a different file or re-export your document.",
            "tips": [
                "Try re-saving the PDF from the original source",
                "Check if the file downloaded completely",
                "Use a different PDF file if available"
            ]
        },
        PDFErrorType.ENCRYPTED: {
            "title": "Password-Protected PDF",
            "body": "This PDF is password-protected or encrypted. Please remove the password protection and try again.",
            "tips": [
                "Remove password protection from the PDF",
                "Export a new PDF without security settings",
                "Use the original source file (DOCX, DOC) instead"
            ]
        },
        PDFErrorType.NO_TEXT: {
            "title": "No Text Found",
            "body": "We couldn't find any extractable text in this PDF. The file might be empty or contain only images.",
            "tips": [
                "Ensure the PDF contains actual text content",
                "Try exporting from the original source file",
                "Use a text-based format like DOCX or TXT"
            ]
        },
        PDFErrorType.IMAGE_ONLY: {
            "title": "Unreadable PDF",
            "body": "We couldn't read any text in this PDF. It looks scanned or exported as images, so our robots can't parse it. Please upload a text-based PDF (export with real text), or share a DOCX/RTF.",
            "tips": [
                "Export from design tools with \"text as text\" (avoid outlining)",
                "Avoid scans/screenshots without OCR",
                "Try the original source file (DOCX, DOC, Google Docs)"
            ]
        },
        PDFErrorType.UNKNOWN: {
            "title": "PDF Processing Error",
            "body": "We encountered an unexpected error while processing this PDF. Please try a different file format.",
            "tips": [
                "Try uploading a DOCX or TXT file instead",
                "Re-export the PDF from the original source",
                "Check if the file is a valid PDF"
            ]
        }
    }
    
    return error_messages.get(error_type, error_messages[PDFErrorType.UNKNOWN])
