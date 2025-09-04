#!/usr/bin/env python3
"""
Simple test to verify the system is working
"""

import sys
import os
sys.path.append('api')

def test_imports():
    """Test if all modules can be imported"""
    try:
        from api.document_preflight import preflight_document
        print("✅ Preflight system imported successfully")
        
        from api.preflight_types import USER_MESSAGE
        print("✅ Preflight types imported successfully")
        
        from api.simple_smart_extractor import SimpleSmartExtractor
        print("✅ Smart extractor imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_preflight():
    """Test preflight with a simple text file"""
    try:
        from api.document_preflight import preflight_document
        
        # Create a simple text file
        test_content = b"UX Designer with experience in user research and wireframes"
        
        result = preflight_document(test_content, "test.txt")
        print(f"✅ Preflight test: ok={result.ok}")
        
        if result.details:
            print(f"   Text chars: {result.details.total_text_chars}")
            print(f"   Triggers: {result.details.triggers}")
        
        return result.ok
    except Exception as e:
        print(f"❌ Preflight test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing ATS Resume Checker System")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return
    
    # Test preflight
    if not test_preflight():
        print("❌ Preflight tests failed")
        return
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    main()

