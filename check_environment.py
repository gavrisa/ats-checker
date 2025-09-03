#!/usr/bin/env python3
"""
Quick script to check if the ATS Checker test environment is running
"""

import requests
import sys

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, f"✅ {name} is running at {url}"
        else:
            return False, f"⚠️  {name} responded with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"❌ {name} is not running at {url}"
    except Exception as e:
        return False, f"❌ Error checking {name}: {e}"

def main():
    """Check both services"""
    print("🔍 ATS Checker Environment Status Check")
    print("=" * 40)
    
    services = [
        ("http://localhost:8000/health", "Backend API"),
        ("http://localhost:3000", "Frontend")
    ]
    
    all_running = True
    
    for url, name in services:
        is_running, message = check_service(url, name)
        print(message)
        if not is_running:
            all_running = False
    
    print("\n" + "=" * 40)
    
    if all_running:
        print("🎉 All services are running!")
        print("\n🌐 You can access:")
        print("   • Main App: http://localhost:3000")
        print("   • Backend API: http://localhost:8000")
        print("   • Test Interface: http://localhost:8000/test")
    else:
        print("⚠️  Some services are not running.")
        print("\n🔧 To start the environment:")
        print("   • Run: ./start_test_environment.sh")
        print("   • Or start manually:")
        print("     Backend:  cd api && python3 main.py")
        print("     Frontend: cd web && npm run dev")
    
    return all_running

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

