#!/usr/bin/env python3
"""
Simple test script for the new ATS Checker backend
"""

import requests
import json

def test_keyword_extraction():
    """Test the keyword extraction endpoint"""
    url = "http://localhost:8000/extract-keywords"
    
    # Sample job description with realistic content
    jd_text = """
    Senior UX Designer
    
    We are seeking a talented UX Designer who will be responsible for:
    
    Key Responsibilities:
    - Conduct user research and usability testing
    - Create wireframes and interactive prototypes using Figma
    - Design user interfaces and user experiences
    - Implement accessibility compliance standards
    - Develop design systems and component libraries
    - Collaborate with cross-functional teams
    - Execute design thinking methodologies
    - Support product development processes
    
    Required Skills:
    - User research methodologies
    - Wireframing and prototyping
    - Figma and design tools
    - Accessibility standards (WCAG)
    - Information architecture
    - User journey mapping
    - Design systems
    - Usability testing
    
    Experience:
    - 5+ years in UX design
    - Experience with SaaS platforms
    - Knowledge of user-centered design
    - Understanding of design principles
    """
    
    # Sample CV text
    cv_text = """
    UX Designer with 5 years of experience in user research and design.
    Proficient in Figma, user research, wireframing, and accessibility.
    Experience with design systems and usability testing.
    Created wireframes and prototypes for multiple projects.
    Conducted user research and usability studies.
    Implemented accessibility standards in all designs.
    """
    
    data = {
        "jd_text": jd_text,
        "cv_text": cv_text
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Keyword extraction successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print(f"All Keywords: {result.get('all_keywords', [])[:15]}...")
            print(f"Matched Keywords: {result.get('matched_keywords', [])}")
            print(f"Missing Keywords: {result.get('missing_keywords', [])}")
            print(f"Bullet Suggestions: {result.get('bullet_suggestions', [])}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test the health endpoint"""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check: {result}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing new ATS Checker backend with improved filtering...\n")
    
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing keyword extraction...")
    test_keyword_extraction()
    print()
    
    print("�� Test completed!")
