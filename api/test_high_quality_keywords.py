#!/usr/bin/env python3
"""
Test script for the new high-quality JD keyword extraction system
"""

import requests
import json

def test_high_quality_keywords():
    """Test the new high-quality keyword extraction system"""
    url = "http://localhost:8000/extract-keywords"
    
    # Test Case A: Senior Product Designer for consumer apps
    print("🧪 TEST CASE A: Senior Product Designer for consumer apps")
    print("=" * 60)
    
    jd_text_a = """
    Senior Product Designer for consumer apps. Fully remote, Europe. Please join our platform. 
    Work on end-to-end design in Figma, run discovery and usability testing.
    """
    
    cv_text_a = """
    UX Designer with experience in Figma, user research, and design systems.
    """
    
    data_a = {
        "jd_text": jd_text_a,
        "cv_text": cv_text_a
    }
    
    try:
        response = requests.post(url, data=data_a)
        if response.status_code == 200:
            result = response.json()
            print("✅ Test A successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS:")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords, 1):
                print(f"  {i:2d}. {keyword}")
            print()
            
            print("🎯 DOMAIN TAGS:")
            domain_tags = result.get('domain_tags', [])
            for tag in domain_tags:
                print(f"  🏷️  {tag}")
            print()
            
            print("👔 ROLE TAGS:")
            role_tags = result.get('role_tags', [])
            for tag in role_tags:
                print(f"  👔 {tag}")
            print()
            
            print("❌ DROPPED EXAMPLES:")
            dropped = result.get('dropped_examples', [])
            for example in dropped:
                print(f"  ❌ {example}")
            print()
            
            print("📋 EXPECTED RESULTS FOR TEST A:")
            print("✅ KEEP: end-to-end design, figma, discovery, usability testing")
            print("❌ DROP: senior product, product designer, consumer apps (→ domain_tags)")
            print("❌ DROP: fully remote, europe, please, join, platform")
            print("❌ NO FRAGMENTS: end design, look, that should never appear")
            print()
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case B: Lead accessibility and interaction design
    print("🧪 TEST CASE B: Lead accessibility and interaction design")
    print("=" * 60)
    
    jd_text_b = """
    Lead accessibility and interaction design for mobile app; collaborate with engineers; 
    create wireframes and user journeys.
    """
    
    cv_text_b = """
    Designer with experience in accessibility, interaction design, and mobile app design.
    """
    
    data_b = {
        "jd_text": jd_text_b,
        "cv_text": cv_text_b
    }
    
    try:
        response = requests.post(url, data=data_b)
        if response.status_code == 200:
            result = response.json()
            print("✅ Test B successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS:")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords, 1):
                print(f"  {i:2d}. {keyword}")
            print()
            
            print("📋 EXPECTED RESULTS FOR TEST B:")
            print("✅ KEEP: accessibility, interaction design, mobile app design, wireframes, user journeys")
            print("❌ DROP: lone mobile, collaborate, engineers")
            print()
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case C: Discovery → prototyping → usability testing
    print("🧪 TEST CASE C: Discovery → prototyping → usability testing")
    print("=" * 60)
    
    jd_text_c = """
    Own discovery → prototyping → usability testing; build design system tokens in Figma.
    """
    
    cv_text_c = """
    UX Designer with experience in discovery, prototyping, and design systems.
    """
    
    data_c = {
        "jd_text": jd_text_c,
        "cv_text": cv_text_c
    }
    
    try:
        response = requests.post(url, data=data_c)
        if response.status_code == 200:
            result = response.json()
            print("✅ Test C successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS:")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords, 1):
                print(f"  {i:2d}. {keyword}")
            print()
            
            print("📋 EXPECTED RESULTS FOR TEST C:")
            print("✅ KEEP: discovery, prototyping, usability testing, design system, design tokens, figma")
            print("❌ DROP: standalone system, tokens, app")
            print()
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case D: Adult content moderation
    print("🧪 TEST CASE D: Adult content moderation")
    print("=" * 60)
    
    jd_text_d = """
    Experience with adult content moderation is a plus.
    """
    
    cv_text_d = """
    Content moderator with experience in various platforms.
    """
    
    data_d = {
        "jd_text": jd_text_d,
        "cv_text": cv_text_d
    }
    
    try:
        response = requests.post(url, data=data_d)
        if response.status_code == 200:
            result = response.json()
            print("✅ Test D successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS:")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords, 1):
                print(f"  {i:2d}. {keyword}")
            print()
            
            print("🎯 DOMAIN TAGS:")
            domain_tags = result.get('domain_tags', [])
            for tag in domain_tags:
                print(f"  🏷️  {tag}")
            print()
            
            print("📋 EXPECTED RESULTS FOR TEST D:")
            print("✅ KEYWORDS: none (unless explicitly whitelisted)")
            print("✅ DOMAIN_TAGS: ['adult content']")
            print()
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
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
    print("🧪 Testing High-Quality JD Keyword Extraction System\n")
    
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing high-quality keyword extraction...")
    test_high_quality_keywords()
    print()
    
    print("🎯 High-quality keyword extraction test completed!")
    print("\n📋 ACCEPTANCE CRITERIA:")
    print("✅ Only keep candidates from allowed categories (methods, tools, deliverables, process)")
    print("✅ Drop all HR/marketing terms (fully remote, europe, please, join)")
    print("✅ Drop generic nouns unless in allowed bigrams (mobile app design)")
    print("✅ Drop fragments & filler (end design, look, that)")
    print("✅ Drop role titles (senior product designer)")
    print("✅ Extract domain_tags and role_tags separately")
    print("✅ No duplicates/near-duplicates")
    print("✅ Clean, professional keyword list")

