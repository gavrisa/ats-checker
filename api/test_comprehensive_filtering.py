#!/usr/bin/env python3
"""
Comprehensive test script to demonstrate the new blacklist/whitelist filtering system
"""

import requests
import json

def test_comprehensive_filtering():
    """Test the comprehensive filtering system"""
    url = "http://localhost:8000/extract-keywords"
    
    # Comprehensive job description with many blacklist and whitelist items
    jd_text = """
    Senior UX Designer - Product Team
    
    We are looking for a talented UX Designer who will be responsible for:
    
    Key Responsibilities:
    - You will conduct user research and usability testing
    - You are expected to create wireframes and interactive prototypes using Figma
    - You will design user interfaces and user experiences
    - You must implement accessibility compliance standards (WCAG)
    - You should develop design systems and component libraries
    - You will collaborate with cross-functional teams
    - You are responsible for executing design thinking methodologies
    - You will support product development processes
    
    Required Skills & Experience:
    - Strong background in user research methodologies
    - Excellent wireframing and prototyping skills
    - Proven experience with Figma, Sketch, and Adobe XD
    - Good knowledge of accessibility standards and compliance
    - Great understanding of information architecture
    - Strong user journey mapping experience
    - Excellent design system expertise
    - Good usability testing background
    
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
    - We are passionate about user-centered design
    - We work together as a team
    - We believe in continuous improvement
    - We support each other's growth
    - We are committed to excellence
    - We value collaboration and teamwork
    - We are part of a larger organization
    - We contribute to company success
    
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
    """
    
    # Sample CV text
    cv_text = """
    UX Designer with 5 years of experience in user research and design.
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
            print("✅ Comprehensive filtering test successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS (Top 20):")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords[:20], 1):
                # Mark whitelist items
                if keyword in ['figma', 'sketch', 'adobe xd', 'miro', 'jira', 'confluence', 
                              'zeplin', 'notion', 'user research', 'usability testing', 
                              'accessibility', 'design system', 'cross-functional', 'product']:
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
    print("🧪 Testing Comprehensive Blacklist/Whitelist Filtering System\n")
    
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing comprehensive filtering...")
    test_comprehensive_filtering()
    print()
    
    print("🎯 Comprehensive test completed!")
    print("\n📋 FILTERING RESULTS SUMMARY:")
    print("✅ WHITELIST items should appear and be prioritized")
    print("❌ BLACKLIST items should be filtered out")
    print("🎯 Only meaningful, job-specific keywords should remain")

