#!/usr/bin/env python3
"""
Test script for the document preflight system
"""

import sys
import os
sys.path.append('api')

from api.document_preflight import preflight_document
from api.preflight_types import USER_MESSAGE

def test_file(filename):
    """Test a file with the preflight system"""
    print(f"\n=== Testing {filename} ===")
    
    try:
        with open(filename, 'rb') as f:
            file_content = f.read()
        
        result = preflight_document(file_content, filename)
        
        print(f"OK: {result.ok}")
        if result.user_message:
            print(f"User Message: {result.user_message[:100]}...")
        
        if result.details:
            print(f"MIME: {result.details.mime}")
            print(f"Pages: {result.details.pages}")
            print(f"Text chars: {result.details.total_text_chars}")
            print(f"Text pages: {result.details.text_pages}")
            print(f"Text density: {result.details.text_density}")
            print(f"Images: {result.details.images_total}")
            print(f"Encrypted: {result.details.encrypted}")
            print(f"Triggers: {result.details.triggers}")
        
        return result
        
    except FileNotFoundError:
        print(f"File {filename} not found")
        return None
    except Exception as e:
        print(f"Error testing {filename}: {e}")
        return None

def main():
    """Test various files"""
    print("Document Preflight System Test")
    print("=" * 40)
    
    # Test files
    test_files = [
        "figma_test.pdf",
        "minimal_test.pdf", 
        "test_resume.txt",
        "test_corrupted.pdf"
    ]
    
    results = {}
    for filename in test_files:
        result = test_file(filename)
        if result:
            results[filename] = result
    
    print("\n=== Summary ===")
    for filename, result in results.items():
        status = "✅ PASS" if result.ok else "❌ BLOCK"
        print(f"{filename}: {status}")
        if not result.ok and result.details:
            print(f"  Triggers: {', '.join(result.details.triggers)}")

if __name__ == "__main__":
    main()
