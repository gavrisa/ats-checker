#!/usr/bin/env python3
"""
Test script for the ATS Keyword Extractor endpoint
"""

import requests
import json

# Sample job description (UX Designer role)
JD_TEXT = """
Senior UX Designer

We are looking for a Senior UX Designer to join our product development team. You will be responsible for creating user-centered design solutions that enhance the user experience across our SaaS platform.

Key Responsibilities:
- Conduct user research and usability testing to understand user needs and pain points
- Create wireframes, interactive prototypes, and user journeys to communicate design concepts
- Develop personas and experience maps to guide design decisions
- Collaborate with product development teams to implement design solutions
- Ensure accessibility compliance (WCAG) across all design deliverables
- Conduct qualitative and quantitative research to validate design decisions
- Create design systems and information architecture for scalable solutions
- Perform heuristics evaluation and A/B testing to optimize user experience
- Lead stakeholder alignment sessions to gather requirements and feedback
- Implement mixed-methods research approaches for comprehensive insights
- Work with cross-functional collaboration teams
- Create service blueprint and journey analytics

Requirements:
- 5+ years of experience in UX design and user research
- Proficiency in design tools and prototyping software
- Strong understanding of accessibility standards and best practices
- Experience with task flows and journey analytics
- Knowledge of service blueprint methodologies
- Excellent communication and collaboration skills
- Experience working with cross-functional teams
- Portfolio demonstrating user-centered design projects
"""

# Sample CV text
CV_TEXT = """
JOHN DOE
UX Designer & Researcher

EXPERIENCE

Senior UX Designer | TechCorp | 2020-2023
- Led user research initiatives using qualitative and quantitative methods
- Created wireframes and interactive prototypes for mobile applications
- Developed user personas and journey maps for e-commerce platform
- Conducted usability testing sessions with 50+ participants
- Implemented accessibility improvements achieving WCAG 2.1 AA compliance
- Collaborated with product teams to deliver user-centered solutions
- Created design systems and component libraries for consistency

UX Designer | StartupXYZ | 2018-2020
- Designed user interfaces for web applications
- Conducted user interviews and surveys for product validation
- Created wireframes and mockups using Figma and Sketch
- Performed competitive analysis and market research
- Worked with development teams to implement design solutions
- Established design guidelines and best practices

SKILLS
- User Research & Usability Testing
- Wireframing & Prototyping
- Design Systems & Information Architecture
- Accessibility (WCAG) Compliance
- Figma, Sketch, Adobe Creative Suite
- Qualitative & Quantitative Research Methods
- Stakeholder Management & Collaboration
- A/B Testing & Analytics
"""

def test_ats_extractor():
    """Test the ATS keyword extractor endpoint"""
    
    url = "http://localhost:8000/extract-keywords"
    
    data = {
        "jd_text": JD_TEXT,
        "cv_text": CV_TEXT
    }
    
    try:
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ ATS Keyword Extraction Results:")
            print("=" * 50)
            
            print(f"\n📋 All Keywords ({len(result['all_keywords'])}):")
            for i, keyword in enumerate(result['all_keywords'], 1):
                print(f"  {i:2d}. {keyword}")
            
            print(f"\n✅ Matched Keywords ({len(result['matched_keywords'])}):")
            for i, keyword in enumerate(result['matched_keywords'], 1):
                print(f"  {i:2d}. {keyword}")
            
            print(f"\n❌ Missing Keywords ({len(result['missing_keywords'])}):")
            for i, keyword in enumerate(result['missing_keywords'], 1):
                print(f"  {i:2d}. {keyword}")
            
            print(f"\n💡 Bullet Suggestions ({len(result['bullet_suggestions'])}):")
            for i, suggestion in enumerate(result['bullet_suggestions'], 1):
                print(f"  {i}. {suggestion}")
            
            print(f"\n🔍 Debug Info:")
            print(f"  Dropped examples: {result['debug']['dropped_examples']}")
            print(f"  Kept examples: {result['debug']['kept_examples']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8000")
        print("   Run: cd api && python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ats_extractor()
