#!/usr/bin/env python3
"""
Test script specifically for deduplication and canonicalization features
"""

import requests
import json

def test_deduplication():
    """Test the new deduplication and canonicalization system"""
    url = "http://localhost:8000/extract-keywords"
    
    # Job description with many duplicate and near-duplicate keywords
    jd_text = """
    Senior Product Designer - UX Team
    
    We are looking for a talented Senior Product Designer who will be responsible for:
    
    Key Responsibilities:
    - You will conduct user research and usability testing from day one
    - You are expected to create wireframes and interactive prototypes using Figma
    - You must implement accessibility compliance standards (WCAG) starting day one
    - You will collaborate with cross-functional teams on day one
    - You are responsible for executing design thinking methodologies
    - You will support product development processes from day one
    
    What You Will Do:
    - Make design decisions based on user insights
    - Create and manage design documentation
    - Work closely with product managers and developers
    - Help establish design processes and workflows
    - Support team collaboration and communication
    - Give presentations to stakeholders
    - Take ownership of design quality
    - Show leadership in design initiatives
    
    Our Team Values:
    - We are passionate about user-center design
    - We work together as a team
    - We believe in continuous improvement
    - We support each other's growth
    - We are committed to excellence
    - We value collaboration and teamwork
    - We are part of a larger organization
    - We contribute to company success
    
    Required Skills:
    - Strong background in user research methodologies
    - Excellent wireframing and prototyping skills
    - Proven experience with Figma, Sketch, and Adobe XD
    - Good knowledge of accessibility standards and compliance
    - Great understanding of information architecture
    - Strong user journey mapping experience
    - Excellent design system expertise
    - Good usability testing background
    
    Tools & Technologies:
    - Figma, Sketch, Adobe XD
    - Miro for collaboration
    - Jira for project management
    - Confluence for documentation
    - Zeplin for handoffs
    - Notion for knowledge sharing
    
    Methodologies:
    - User research and hypothesis testing
    - Discovery and ideation processes
    - Prototyping and validation
    - A/B testing and optimization
    - Data analytics and insights
    - Agile and Scrum workflows
    
    Additional Requirements:
    - Senior product design experience
    - Senior product designer skills
    - Product designer expertise
    - Senior designer capabilities
    - Designer with senior experience
    - Product design senior level
    - Senior level product design
    - Design senior product
    - Product senior design
    - Senior product design
    - Product design senior
    - Senior design product
    - Design product senior
    - Senior product design
    - Product senior design
    - Design senior product
    - Senior design product
    - Product design senior
    - Senior product design
    - Product senior design
    - Design product senior
    - Senior product design
    - Product design senior
    - Senior design product
    - Product senior design
    - Design senior product
    - Senior product design
    - Product senior design
    - Design product senior
    - Senior product design
    - Product design senior
    """
    
    # Sample CV text
    cv_text = """
    Senior Product Designer with 8 years of experience in user research and design.
    Proficient in Figma, user research, wireframing, and accessibility.
    Experience with design systems and usability testing.
    Created wireframes and prototypes for multiple projects.
    Conducted user research and usability studies.
    Implemented accessibility standards in all designs.
    Worked with cross-functional teams on product development.
    Used Figma, Sketch, and Adobe XD for design work.
    Applied user-centered design methodologies.
    Conducted A/B testing and optimization experiments.
    """
    
    data = {
        "jd_text": jd_text,
        "cv_text": cv_text
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Deduplication test successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS (Top 30):")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords, 1):
                # Mark whitelist items
                if keyword in ['figma', 'sketch', 'adobe xd', 'miro', 'jira', 'confluence', 
                              'zeplin', 'notion', 'user research', 'usability testing', 
                              'accessibility', 'design system', 'cross-functional', 'product',
                              'user-centered', 'journey mapping', 'ideation', 'validation',
                              'optimization', 'data', 'agile', 'scrum']:
                    print(f"  {i:2d}. ✅ {keyword} (WHITELIST)")
                else:
                    print(f"  {i:2d}. {keyword}")
            print()
            
            print("🎯 MATCHED KEYWORDS:")
            matched = result.get('matched_keywords', [])
            for keyword in matched:
                print(f"  ✅ {keyword}")
            print()
            
            print("❌ MISSING KEYWORDS (Top 7):")
            missing = result.get('missing_keywords', [])
            for keyword in missing:
                print(f"  ❌ {keyword}")
            print()
            
            print("💡 BULLET SUGGESTIONS:")
            suggestions = result.get('bullet_suggestions', [])
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
            
            # Check for duplicates
            print("\n🔍 DEDUPLICATION ANALYSIS:")
            keyword_set = set(all_keywords)
            if len(keyword_set) == len(all_keywords):
                print("✅ No duplicate keywords found!")
            else:
                print(f"❌ Found {len(all_keywords) - len(keyword_set)} duplicate keywords")
            
            # Check for near-duplicates (similar phrases)
            print("\n🔍 NEAR-DUPLICATE CHECK:")
            near_duplicates = []
            for i, kw1 in enumerate(all_keywords):
                for j, kw2 in enumerate(all_keywords[i+1:], i+1):
                    # Check for substring relationships
                    if kw1 in kw2 or kw2 in kw1:
                        near_duplicates.append((kw1, kw2))
            
            if near_duplicates:
                print(f"❌ Found {len(near_duplicates)} potential near-duplicates:")
                for kw1, kw2 in near_duplicates[:10]:  # Show first 10
                    print(f"  - '{kw1}' vs '{kw2}'")
            else:
                print("✅ No obvious near-duplicates found!")
            
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
    print("🧪 Testing Advanced Deduplication & Canonicalization System\n")
    
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing deduplication...")
    test_deduplication()
    print()
    
    print("🎯 Deduplication test completed!")
    print("\n📋 EXPECTED IMPROVEMENTS:")
    print("✅ No duplicate keywords (e.g., 'senior product' appearing multiple times)")
    print("✅ No near-duplicate keywords (e.g., 'senior product' vs 'senior product designer')")
    print("✅ Fragmentary phrases dropped (e.g., 'that', 'products that', 'looking portfolios')")
    print("✅ Canonical forms preferred (e.g., 'product design' over 'end product design')")
    print("✅ At most one canonical keyword per concept")
    print("✅ Clean, professional keyword list")



