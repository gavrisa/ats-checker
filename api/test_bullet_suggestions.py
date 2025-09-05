#!/usr/bin/env python3
"""
Test script for the new recruiter-friendly, ATS-optimized bullet suggestion system
"""

import requests
import json

def test_bullet_suggestions():
    """Test the new bullet suggestion system"""
    url = "http://localhost:8000/extract-keywords"
    
    # Job description with many missing keywords to test bullet generation
    jd_text = """
    Senior UX Designer - Product Team
    
    We are looking for a talented UX Designer who will be responsible for:
    
    Key Responsibilities:
    - Conduct user research and usability testing from day one
    - Create wireframes and interactive prototypes using Figma
    - Implement accessibility compliance standards (WCAG) starting day one
    - Collaborate with cross-functional teams on day one
    - Execute design thinking methodologies
    - Support product development processes from day one
    
    What You Will Do:
    - Make design decisions based on user insights
    - Create and manage design documentation
    - Work closely with product managers and developers
    - Help establish design processes and workflows
    - Support team collaboration and communication
    - Give presentations to stakeholders
    - Take ownership of design quality
    - Show leadership in design initiatives
    
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
    """
    
    # Sample CV text (minimal to generate many missing keywords)
    cv_text = """
    UX Designer with 3 years of experience in basic design work.
    Proficient in basic wireframing and some prototyping.
    Experience with design documentation.
    Created some wireframes for projects.
    Worked with design teams.
    Used basic design tools.
    """
    
    data = {
        "jd_text": jd_text,
        "cv_text": cv_text
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Bullet suggestion test successful!")
            print(f"ATS Score: {result.get('score', 'N/A')}")
            print(f"Text Similarity: {result.get('textSimilarity', 'N/A')}%")
            print(f"Keyword Coverage: {result.get('keywordCoverage', 'N/A')}%")
            print()
            
            print("🔍 EXTRACTED KEYWORDS (Top 20):")
            all_keywords = result.get('all_keywords', [])
            for i, keyword in enumerate(all_keywords[:20], 1):
                print(f"  {i:2d}. {keyword}")
            print()
            
            print("🎯 MATCHED KEYWORDS:")
            matched = result.get('matched_keywords', [])
            for keyword in matched:
                print(f"  ✅ {keyword}")
            print()
            
            print("❌ MISSING KEYWORDS (Top 10):")
            missing = result.get('missing_keywords', [])
            for keyword in missing:
                print(f"  ❌ {keyword}")
            print()
            
            print("💡 NEW RECRUITER-FRIENDLY BULLET SUGGESTIONS:")
            print("=" * 60)
            suggestions = result.get('bullet_suggestions', [])
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
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
            
            # Analyze bullet quality
            print("📊 BULLET QUALITY ANALYSIS:")
            print("=" * 60)
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\nBullet {i}: {suggestion}")
                
                # Check for required components
                has_action_verb = any(verb in suggestion for verb in [
                    "Led", "Designed", "Optimized", "Implemented", "Conducted", 
                    "Improved", "Developed", "Created", "Built", "Established"
                ])
                
                has_missing_keyword = any(keyword.lower() in suggestion.lower() for keyword in missing[:5])
                
                has_context = any(word in suggestion.lower() for word in [
                    "workshops", "sessions", "initiatives", "standards", "principles", 
                    "prototypes", "systems", "processes", "methodologies"
                ])
                
                has_purpose = any(word in suggestion.lower() for word in [
                    "improve", "enhance", "accelerate", "reduce", "increase", 
                    "streamline", "optimize", "validate", "ensure"
                ])
                
                has_impact = any(word in suggestion.lower() for word in [
                    "%", "faster", "reduced", "improved", "accelerated", "cut", "half"
                ])
                
                print(f"  ✅ Action verb: {has_action_verb}")
                print(f"  ✅ Missing keyword: {has_missing_keyword}")
                print(f"  ✅ Context: {has_context}")
                print(f"  ✅ Purpose: {has_purpose}")
                print(f"  ✅ Impact/result: {has_impact}")
                
                # Overall quality score
                quality_score = sum([has_action_verb, has_missing_keyword, has_context, has_purpose, has_impact])
                print(f"  📊 Quality Score: {quality_score}/5")
            
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
    print("🧪 Testing New Recruiter-Friendly Bullet Suggestion System\n")
    
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing bullet suggestions...")
    test_bullet_suggestions()
    print()
    
    print("🎯 Bullet suggestion test completed!")
    print("\n📋 ACCEPTANCE CRITERIA:")
    print("✅ Every bullet must include: action verb + missing keyword + context + purpose + measurable result")
    print("✅ No fluff or filler sentences")
    print("✅ Output: 3–5 smart bullets per resume")
    print("✅ Tone matches professional resume standards")
    print("✅ Always integrate job-related terminology")
    print("✅ Make sure bullets look like strong real resume lines")








