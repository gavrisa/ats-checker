#!/usr/bin/env python3
"""
Test script to verify the ATS Checker test environment is working correctly
"""

import requests
import time
import sys

def test_backend():
    """Test backend connectivity and health"""
    print("🔧 Testing Backend API...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health check: {data}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
        # Test analyze endpoint (should return 400 for missing data, which is expected)
        response = requests.post("http://localhost:8000/analyze", timeout=10)
        if response.status_code in [400, 422]:  # Expected for missing data
            print("✅ Backend analyze endpoint responding (400 expected for missing data)")
        else:
            print(f"⚠️  Backend analyze endpoint: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend at http://localhost:8000")
        print("   Make sure the backend is running: cd api && python3 main.py")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_frontend():
    """Test frontend connectivity"""
    print("\n🎨 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to frontend at http://localhost:3000")
        print("   Make sure the frontend is running: cd web && npm run dev")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    print("\n📤 Testing File Upload...")
    
    try:
        # Create a simple test file
        test_content = "This is a test resume content for testing purposes."
        
        # Test the upload endpoint
        files = {'resume_file': ('test_resume.txt', test_content, 'text/plain')}
        data = {'job_description': 'Test job description for testing purposes.'}
        
        response = requests.post("http://localhost:8000/analyze", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload and analysis working!")
            print(f"   ATS Score: {result.get('score', 'N/A')}")
            print(f"   Keywords Found: {len(result.get('all_keywords', []))}")
            print(f"   Bullet Suggestions: {len(result.get('bullet_suggestions', []))}")
            return True
        else:
            print(f"⚠️  File upload test: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ File upload test error: {e}")
        return False

def test_keyword_extraction():
    """Test keyword extraction functionality"""
    print("\n🔍 Testing Keyword Extraction...")
    
    try:
        # Test the extract-keywords endpoint
        data = {
            'jd_text': 'Senior UX Designer with experience in Figma, user research, and accessibility standards.',
            'cv_text': 'UX Designer with 3 years of experience in basic design work and prototyping.'
        }
        
        response = requests.post("http://localhost:8000/extract-keywords", data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Keyword extraction working!")
            print(f"   Keywords Found: {len(result.get('all_keywords', []))}")
            print(f"   Domain Tags: {result.get('domain_tags', [])}")
            print(f"   Role Tags: {result.get('role_tags', [])}")
            print(f"   Bullet Suggestions: {len(result.get('bullet_suggestions', []))}")
            return True
        else:
            print(f"⚠️  Keyword extraction test: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Keyword extraction test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ATS Checker Test Environment Verification")
    print("=" * 50)
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    tests = [
        ("Backend API", test_backend),
        ("Frontend", test_frontend),
        ("File Upload", test_file_upload),
        ("Keyword Extraction", test_keyword_extraction)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your test environment is working correctly.")
        print("\n🌐 You can now access:")
        print("   • Main App: http://localhost:3000")
        print("   • Backend API: http://localhost:8000")
        print("   • Test Interface: http://localhost:8000/test")
    else:
        print("⚠️  Some tests failed. Check the logs and ensure both services are running.")
        print("\n🔧 Troubleshooting:")
        print("   • Backend: cd api && python3 main.py")
        print("   • Frontend: cd web && npm run dev")
        print("   • Check ports: lsof -i :3000 && lsof -i :8000")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

