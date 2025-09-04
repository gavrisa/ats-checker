#!/usr/bin/env python3
"""
Test script for PDF validation functionality.
Tests various PDF scenarios to ensure proper error detection and handling.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_validator import PDFValidator, get_pdf_error_message, PDFErrorType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_pdf_content():
    """Create a simple test PDF content for testing"""
    # This is a minimal PDF structure for testing
    # In a real test, you'd use actual PDF files
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000368 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
465
%%EOF"""

def create_corrupted_pdf_content():
    """Create corrupted PDF content for testing"""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000368 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
465
%%EOF"""

def create_empty_pdf_content():
    """Create PDF with no text content"""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
>>
>>
endobj

4 0 obj
<<
/Length 0
>>
stream
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
325
%%EOF"""

def test_pdf_validator():
    """Test the PDF validator with various scenarios"""
    logger.info("🧪 Starting PDF validation tests...")
    
    validator = PDFValidator()
    
    # Test 1: Valid PDF with text
    logger.info("\n📄 Test 1: Valid PDF with text")
    valid_pdf = create_test_pdf_content()
    result = validator.validate_pdf(valid_pdf, "test_valid.pdf")
    
    if result.is_valid:
        logger.info("✅ Valid PDF test passed")
        logger.info(f"   - Extracted text: '{result.extracted_text}'")
        logger.info(f"   - Page count: {result.page_count}")
    else:
        logger.error(f"❌ Valid PDF test failed: {result.error_message}")
    
    # Test 2: Empty PDF (no text)
    logger.info("\n📄 Test 2: Empty PDF (no text)")
    empty_pdf = create_empty_pdf_content()
    result = validator.validate_pdf(empty_pdf, "test_empty.pdf")
    
    if not result.is_valid and result.error_type == PDFErrorType.NO_TEXT:
        logger.info("✅ Empty PDF test passed")
        logger.info(f"   - Error type: {result.error_type.value}")
        logger.info(f"   - Error message: {result.error_message}")
    else:
        logger.error(f"❌ Empty PDF test failed: {result.error_message}")
    
    # Test 3: Corrupted PDF
    logger.info("\n📄 Test 3: Corrupted PDF")
    corrupted_pdf = b"Not a valid PDF file content"
    result = validator.validate_pdf(corrupted_pdf, "test_corrupted.pdf")
    
    if not result.is_valid and result.error_type == PDFErrorType.CORRUPT:
        logger.info("✅ Corrupted PDF test passed")
        logger.info(f"   - Error type: {result.error_type.value}")
        logger.info(f"   - Error message: {result.error_message}")
    else:
        logger.error(f"❌ Corrupted PDF test failed: {result.error_message}")
    
    # Test 4: Error message formatting
    logger.info("\n📄 Test 4: Error message formatting")
    for error_type in PDFErrorType:
        error_info = get_pdf_error_message(error_type)
        logger.info(f"   - {error_type.value}:")
        logger.info(f"     Title: {error_info['title']}")
        logger.info(f"     Body: {error_info['body'][:100]}...")
        logger.info(f"     Tips: {len(error_info['tips'])} tips provided")
    
    logger.info("\n🎉 PDF validation tests completed!")

def test_integration_with_main():
    """Test integration with the main API"""
    logger.info("\n🔗 Testing integration with main API...")
    
    try:
        # Import the main module components
        from main import extract_text_from_file
        
        # Test with valid PDF
        valid_pdf = create_test_pdf_content()
        text, file_info = extract_text_from_file(valid_pdf, "test.pdf", "application/pdf")
        
        if file_info.get("text_extractable", False):
            logger.info("✅ Main API integration test passed")
            logger.info(f"   - Extracted text length: {len(text)}")
            logger.info(f"   - File info: {file_info}")
        else:
            logger.error(f"❌ Main API integration test failed: {file_info.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Main API integration test failed with exception: {str(e)}")

if __name__ == "__main__":
    test_pdf_validator()
    test_integration_with_main()

