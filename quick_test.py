#!/usr/bin/env python3
"""
Quick test of the ATS keyword extractor functions
"""

import sys
import os
sys.path.append('api')

# Import the functions directly
from main import extract_ats_keywords, match_keywords_to_cv, generate_bullet_suggestions, get_debug_info

# Sample data
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
"""

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

def test_extractor():
    print("🧪 Testing ATS Keyword Extractor Functions")
    print("=" * 50)
    
    # Extract keywords
    print("\n📋 Extracting keywords from job description...")
    all_keywords = extract_ats_keywords(JD_TEXT)
    print(f"Found {len(all_keywords)} keywords:")
    for i, keyword in enumerate(all_keywords[:10], 1):
        print(f"  {i:2d}. {keyword}")
    
    # Match against CV
    print(f"\n✅ Matching keywords against CV...")
    matching_result = match_keywords_to_cv(all_keywords, CV_TEXT)
    matched = matching_result["matched_keywords"]
    missing = matching_result["missing_keywords"]
    
    print(f"Matched: {len(matched)} keywords")
    for i, keyword in enumerate(matched[:5], 1):
        print(f"  {i}. {keyword}")
    
    print(f"\n❌ Missing: {len(missing)} keywords")
    for i, keyword in enumerate(missing[:5], 1):
        print(f"  {i}. {keyword}")
    
    # Generate bullet suggestions
    print(f"\n💡 Generating bullet suggestions...")
    suggestions = generate_bullet_suggestions(missing[:5])
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Debug info
    print(f"\n🔍 Debug information:")
    debug_info = get_debug_info(JD_TEXT)
    print(f"Dropped examples: {debug_info['dropped_examples'][:3]}")
    print(f"Kept examples: {debug_info['kept_examples'][:3]}")
    
    print(f"\n✅ All functions working correctly!")

if __name__ == "__main__":
    test_extractor()





