#!/usr/bin/env python3
"""
Test runner script for the ATS Checker backend
"""
import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print("❌ FAILED")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ATS Checker Backend Test Suite")
    print("=" * 50)
    
    tests = [
        ("python3 -m pytest tests/test_keyword_extraction.py -v", "Unit Tests - Keyword Extraction"),
        ("python3 -m pytest tests/test_api_endpoints.py -v", "Integration Tests - API Endpoints"),
        ("python3 -m pytest tests/test_performance.py -v", "Performance Tests"),
        ("python3 -m pytest tests/ --tb=short", "All Tests Summary"),
    ]
    
    passed = 0
    total = len(tests)
    
    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 FINAL RESULTS")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working great!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
