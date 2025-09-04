"""
Document Preflight Types and Constants

This module defines the types and constants for the document preflight system
that detects unreadable files before processing.
"""

from typing import Dict, List, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum


class MimeType(str, Enum):
    """Supported MIME types for document preflight"""
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
    UNKNOWN = "unknown"


@dataclass
class PreflightDetails:
    """Internal details for preflight results (never shown to user)"""
    mime: MimeType
    pages: Optional[int] = None  # PDFs only
    total_text_chars: int = 0
    text_pages: Optional[int] = None  # PDFs only
    text_density: Optional[float] = None  # PDFs: chars/page (rounded)
    images_total: Optional[int] = None  # page images (PDF) or drawings/pics (DOCX)
    encrypted: Optional[bool] = None
    triggers: List[str] = None
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []


@dataclass
class PreflightResult:
    """Result of document preflight check"""
    ok: bool  # true => continue; false => block
    user_message: Optional[str] = None  # present only when ok=false
    details: Optional[PreflightDetails] = None  # internal, never shown to user


# Single user-facing message (EN only, keep line breaks & bullets)
USER_MESSAGE = """Most likely this document isn't machine-readable — the bots are seeing vibes, not text.

Possible reasons:
• It's a scan (text is just an image).
• The text was outlined (not selectable).
• The file is encrypted/password-protected.
• The document is corrupted or exported oddly.
• Characters are spaced weirdly from a design export (hello, Figma).

Please re-upload a document with real, selectable text (no screenshots/outlines), then try again.

Best places to create your CV (for ATS):
• Google Docs or Microsoft Word → Export/Save as PDF (text remains selectable).
• Notion → Export as PDF (ensure pages aren't images-only).
• Adobe InDesign → Export PDF with fonts embedded; avoid outlining text.

Using Canva? Recommended export:
• File → Download → PDF Print (or PDF Standard) — both are okay for ATS.
• Do NOT enable "Flatten PDF".
• Skip "Crop marks and bleed" for the ATS version.
• Keep text layers truly text (no outlines/effects that rasterize).
• Quick check: open the PDF and try to select & copy text. If you can, bots can too."""


# Trigger constants for internal detection rules
class Triggers:
    # PDF triggers
    IMAGE_ONLY_NO_TEXT = "image_only_no_text"
    OUTLINED_OR_NO_FONTS = "outlined_or_no_fonts"
    ENCRYPTED_PDF = "encrypted_pdf"
    PARSER_MALFORMED = "parser_malformed"
    LOW_TEXT_RATIO = "low_text_ratio"
    FIGMA_LIKE_SPACING = "figma_like_spacing"
    
    # DOCX triggers
    DOCX_IMAGE_ONLY = "docx_image_only"
    DOCX_LOW_TEXT = "docx_low_text"
    ENCRYPTED_DOCX = "encrypted_docx"
    PARSER_MALFORMED_DOCX = "parser_malformed_docx"
    
    # DOC triggers
    DOC_LOW_TEXT = "doc_low_text"
    ENCRYPTED_DOC = "encrypted_doc"
    PARSER_MALFORMED_DOC = "parser_malformed_doc"

    # General triggers
    FILE_TOO_LARGE = "file_too_large"
    UNSUPPORTED_FORMAT = "unsupported_format"
    INSUFFICIENT_TEXT = "insufficient_text"
    FIGMA_SUSPICIOUS_SIZE = "figma_suspicious_size"
    
    # Figma fragmentation triggers
    FIGMA_LIKE_FRAGMENTATION = "figma_like_fragmentation"
    HIGH_FRAGMENTATION_DENSITY = "high_fragmentation_density"
    PRODUCER_FIGMA_CANVA = "producer_figma_canva"
    UNTAGGED_PDF = "untagged_pdf"
    FIGMA_GAP_PATTERN = "figma_gap_pattern"


# File size and page limits
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
FIGMA_SUSPICIOUS_SIZE = 500 * 1024  # 500KB - Figma exports are often large
MAX_PAGES = 20  # for PDFs

# Text thresholds - Realistic for CVs
MIN_TEXT_CHARS_PDF_SINGLE = 2000  # Single page PDF minimum - lowered for legitimate CVs
MIN_TEXT_CHARS_PDF_MULTI = 80  # Multi-page PDF density per page
MIN_TEXT_CHARS_DOCX_DOC = 200  # DOCX/DOC minimum

# Figma fragmentation detection thresholds (OR logic - any branch can trigger)
SHORT_TOKEN_RATIO_THRESHOLD = 0.01  # 1% short tokens (len<=2, excluding stopwords) - extremely aggressive for Figma detection
SINGLE_CHAR_RATIO_THRESHOLD = 0.005  # 0.5% single character tokens - extremely aggressive for Figma detection
ADJACENT_SHORT_SEQ_RATIO_THRESHOLD = 0.005  # 0.5% consecutive short tokens - extremely aggressive for Figma detection

# Producer-based detection (lower thresholds)
PRODUCER_SHORT_TOKEN_RATIO_THRESHOLD = 0.10  # Lower threshold if Figma/Canva detected - aggressive
PRODUCER_ADJACENT_SHORT_SEQ_THRESHOLD = 0.03  # Lower threshold for adjacent sequences - aggressive

# Gap-based detection - Extremely lenient for legitimate CVs
GAP_PATTERN_THRESHOLD = 0.35  # 35% of gaps > median_char_width * 0.6 - sensitive to Figma exports

# Debug flag for detailed logging
DEBUG_FIGMA_DETECTION = True

# Stopwords to exclude from short token ratio calculation
STOPWORDS = {'a', 'i', 'an', 'to', 'in', 'of', 'on', 'at', 'by', 'or', 'as', 'we', 'be', 'is', 'it', 'for', 'and'}

# Spacing detection thresholds
MAX_SINGLE_CHAR_TOKENS_RATIO = 0.6  # ≥60% tokens length==1
MAX_SPACED_TOKENS_RATIO = 0.3  # ≥30% tokens look like S P A C E D
