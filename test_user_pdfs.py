#!/usr/bin/env python3
"""
Test script to verify PDF validation works with real user PDFs.
This simulates the user's scenario with problematic PDFs.
"""

import requests
import json

def test_pdf_validation():
    """Test PDF validation with various file types"""
    
    base_url = "http://localhost:8000"
    job_description = "We are looking for a Senior UX/UI Designer to lead complex product initiatives. Must have experience with design systems, stakeholder management, usability testing, information architecture, Figma, prototyping, analytics-driven iteration, and accessibility (WCAG)."
    
    print("🧪 Testing PDF Validation System")
    print("=" * 50)
    
    # Test 1: Figma export (should be rejected)
    print("\n1️⃣ Testing Figma Export PDF...")
    try:
        with open('figma_test.pdf', 'rb') as f:
            files = {'resume_file': ('figma_test.pdf', f, 'application/pdf')}
            data = {'job_description': job_description}
            response = requests.post(f"{base_url}/analyze", files=files, data=data)
            result = response.json()
            
            if result.get('status') == 'error' and result.get('error_type') == 'ERR_PDF_IMAGE_ONLY':
                print("✅ PASS: Figma export correctly rejected")
                print(f"   Error: {result.get('message', '')[:80]}...")
                print(f"   Heuristic failures: {result.get('validation_details', {}).get('heuristic_failures', 0)}")
            else:
                print("❌ FAIL: Figma export should have been rejected")
                print(f"   Status: {result.get('status')}")
                print(f"   Error type: {result.get('error_type')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Regular text file (should work)
    print("\n2️⃣ Testing Regular Text File...")
    try:
        with open('test_resume.txt', 'rb') as f:
            files = {'resume_file': ('test_resume.txt', f, 'text/plain')}
            data = {'job_description': job_description}
            response = requests.post(f"{base_url}/analyze", files=files, data=data)
            result = response.json()
            
            if result.get('status') == 'success' or result.get('score') is not None:
                print("✅ PASS: Text file processed successfully")
                print(f"   Score: {result.get('score', 'N/A')}")
                print(f"   Keywords found: {len(result.get('matched_keywords', []))}")
            else:
                print("❌ FAIL: Text file should have been processed")
                print(f"   Status: {result.get('status')}")
                print(f"   Error: {result.get('message', '')[:80]}...")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Create a minimal PDF that should be rejected
    print("\n3️⃣ Testing Minimal PDF (should be rejected)...")
    try:
        # Create a minimal PDF with very little text
        minimal_pdf = b"""%PDF-1.4
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
/Length 15
>>
stream
BT
/F1 12 Tf
72 720 Td
(A) Tj
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
320
%%EOF"""
        
        files = {'resume_file': ('minimal.pdf', minimal_pdf, 'application/pdf')}
        data = {'job_description': job_description}
        response = requests.post(f"{base_url}/analyze", files=files, data=data)
        result = response.json()
        
        if result.get('status') == 'error' and result.get('error_type') == 'ERR_PDF_IMAGE_ONLY':
            print("✅ PASS: Minimal PDF correctly rejected")
            print(f"   Heuristic failures: {result.get('validation_details', {}).get('heuristic_failures', 0)}")
        else:
            print("❌ FAIL: Minimal PDF should have been rejected")
            print(f"   Status: {result.get('status')}")
            print(f"   Error type: {result.get('error_type')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 PDF Validation Test Complete!")
    print("\n💡 The system should now:")
    print("   ✅ Reject Figma exports and image-only PDFs")
    print("   ✅ Process regular text files normally")
    print("   ✅ Show clear error messages for problematic files")

if __name__ == "__main__":
    test_pdf_validation()

