#!/usr/bin/env python3

import requests
import json

def test_keyword_extraction():
    """Test the improved keyword extraction with a sample UX job description"""
    
    # Sample UX job description (similar to what you mentioned)
    job_description = """
    We are looking for a Senior UX Designer to join our team. You will be responsible for:
    
    - Conducting user research and usability testing
    - Creating personas and user journeys
    - Developing wireframes and prototypes
    - Ensuring accessibility compliance (WCAG)
    - Collaborating with product managers and developers
    - Leading design system development
    - Conducting qualitative and quantitative research
    - Working with SaaS solutions and complex products
    - Driving UX maturity across the organization
    - Aligning with stakeholders and product development teams
    - Synthesizing insights from research
    - Creating experience maps and interaction models
    - Leading end-to-end UX processes
    - Building a customer-obsessed design culture
    """
    
    # Sample resume text
    resume_text = """
    UX Designer with 5 years of experience in:
    - UX Design and UX Research
    - Prototyping and wireframing
    - Accessibility (WCAG) implementation
    - Design systems development
    - Workflow simplification
    - Interaction design
    - Information architecture
    - Collaboration with cross-functional teams
    - Leadership in design projects
    - Problem solving and usability testing
    - Iterating on prototypes through discovery and implementation
    - Stakeholder alignment through effective collaboration
    """
    
    try:
        # Test the API
        url = "http://localhost:8000/analyze"
        
        # Create form data
        files = {
            'resume_file': ('test_resume.txt', resume_text, 'text/plain'),
            'job_description': (None, job_description)
        }
        
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Test Successful!")
            print("\n📊 Results:")
            print(f"All Keywords (Top 30): {len(result.get('all_keywords', []))}")
            print(f"Matched Keywords: {len(result.get('matched_keywords', []))}")
            print(f"Missing Keywords (Top 7): {len(result.get('missing_keywords', []))}")
            print(f"Bullet Suggestions: {len(result.get('bullet_suggestions', []))}")
            
            print("\n🔍 All Keywords (Top 30):")
            for i, keyword in enumerate(result.get('all_keywords', [])[:30], 1):
                print(f"  {i:2d}. {keyword}")
            
            print("\n✅ Matched Keywords:")
            for i, keyword in enumerate(result.get('matched_keywords', []), 1):
                print(f"  {i:2d}. {keyword}")
            
            print("\n❌ Missing Keywords (Top 7):")
            for i, keyword in enumerate(result.get('missing_keywords', [])[:7], 1):
                print(f"  {i:2d}. {keyword}")
            
            print("\n💡 Bullet Suggestions:")
            for i, suggestion in enumerate(result.get('bullet_suggestions', []), 1):
                print(f"  {i}. {suggestion}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_keyword_extraction()
