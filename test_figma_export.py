#!/usr/bin/env python3
"""
Test script to simulate Figma export PDF validation.
Creates a PDF that mimics the characteristics of a Figma export.
"""

import io
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_figma_like_pdf():
    """
    Create a PDF that mimics a Figma export - minimal text, likely outlined text.
    This should trigger the image-only detection.
    """
    # This creates a minimal PDF with very little extractable text
    # Similar to what Figma exports look like
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
/Length 20
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hi) Tj
ET
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

def test_figma_export():
    """Test the Figma export scenario"""
    print("🧪 Testing Figma export PDF validation...")
    
    # Import the validator
    from api.pdf_validator import PDFValidator, get_pdf_error_message
    
    # Create validator
    validator = PDFValidator()
    
    # Create Figma-like PDF
    figma_pdf = create_figma_like_pdf()
    
    # Validate it
    result = validator.validate_pdf(figma_pdf, "figma_export.pdf")
    
    print(f"📄 PDF size: {len(figma_pdf)} bytes")
    print(f"📄 Extracted text: '{result.extracted_text}'")
    print(f"📄 Text length: {len(result.extracted_text)}")
    print(f"📄 Is valid: {result.is_valid}")
    
    if not result.is_valid:
        print(f"❌ Error type: {result.error_type.value}")
        print(f"❌ Error message: {result.error_message}")
        
        # Get user-friendly error message
        error_info = get_pdf_error_message(result.error_type)
        print(f"📋 Error title: {error_info['title']}")
        print(f"💬 Error body: {error_info['body']}")
        print(f"💡 Tips:")
        for tip in error_info['tips']:
            print(f"   • {tip}")
        
        if result.validation_details:
            details = result.validation_details
            print(f"🔍 Validation details:")
            print(f"   • Heuristic failures: {details.get('heuristic_failures', 'N/A')}")
            print(f"   • Is mixed document: {details.get('is_mixed_document', 'N/A')}")
            print(f"   • Low density %: {details.get('low_density_percentage', 'N/A'):.1%}")
            print(f"   • Low glyph %: {details.get('low_glyph_percentage', 'N/A'):.1%}")
            print(f"   • High image ratio %: {details.get('high_image_ratio_percentage', 'N/A'):.1%}")
            print(f"   • High vector %: {details.get('high_vector_percentage', 'N/A'):.1%}")
        
        if result.error_type.value == "ERR_PDF_IMAGE_ONLY":
            print("✅ SUCCESS: Figma export correctly detected as image-only!")
        else:
            print(f"❌ FAILED: Expected ERR_PDF_IMAGE_ONLY, got {result.error_type.value}")
    else:
        print("❌ FAILED: Figma export should have been detected as problematic!")

if __name__ == "__main__":
    test_figma_export()

