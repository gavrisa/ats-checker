#!/usr/bin/env python3
"""
Test script for the smart keyword extraction system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_keyword_extractor import SmartKeywordExtractor

def test_smart_keyword_extraction():
    """Test the smart keyword extraction with sample data."""
    
    # Sample job description with noise
    sample_jd = """
    We are looking for a Senior Software Engineer to join our fast-paced team. 
    You will work with stakeholders to build scalable applications using Python, 
    React, and AWS. The ideal candidate has experience with machine learning, 
    data analysis, and cloud infrastructure. You should be able to work 
    collaboratively in a cross-functional environment and have strong 
    communication skills. We offer competitive benefits and a great work-life balance.
    
    Responsibilities:
    - Develop and maintain web applications using Python and React
    - Implement machine learning models and data pipelines
    - Collaborate with product managers and designers
    - Ensure code quality through testing and code reviews
    - Work with AWS services like EC2, S3, and Lambda
    - Participate in agile development processes
    
    Requirements:
    - 5+ years of experience in software development
    - Strong knowledge of Python, JavaScript, and SQL
    - Experience with cloud platforms (AWS, GCP, or Azure)
    - Familiarity with machine learning frameworks (TensorFlow, PyTorch)
    - Knowledge of version control systems (Git)
    - Excellent problem-solving and communication skills
    """
    
    # Sample resume text
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - Developed web applications using Python, Django, and React
    - Implemented REST APIs and microservices architecture
    - Worked with PostgreSQL and Redis databases
    - Used Git for version control and Jenkins for CI/CD
    - Experience with AWS services including EC2 and S3
    - Collaborated with cross-functional teams using Agile methodologies
    
    Skills:
    - Python, JavaScript, SQL, HTML, CSS
    - Django, React, Node.js
    - PostgreSQL, Redis, MongoDB
    - AWS, Docker, Kubernetes
    - Git, Jenkins, Jira
    - Machine Learning, Data Analysis
    """
    
    print("=== Smart Keyword Extraction Test ===\n")
    
    try:
        # Initialize the extractor
        print("Initializing smart keyword extractor...")
        extractor = SmartKeywordExtractor(data_dir="data")
        print("✓ Smart keyword extractor initialized successfully\n")
        
        # Extract keywords from job description
        print("Extracting keywords from job description...")
        jd_keywords = extractor.extract_smart_keywords(sample_jd, 30)
        print(f"✓ Extracted {len(jd_keywords)} keywords from JD")
        print("Top 15 JD keywords:")
        for i, keyword in enumerate(jd_keywords[:15], 1):
            print(f"  {i:2d}. {keyword}")
        print()
        
        # Find matching keywords
        print("Finding matching keywords in resume...")
        matched_keywords, missing_keywords = extractor.find_matching_keywords(sample_resume, jd_keywords)
        print(f"✓ Found {len(matched_keywords)} matched keywords")
        print(f"✓ Found {len(missing_keywords)} missing keywords")
        print()
        
        # Display results
        print("=== RESULTS ===")
        print(f"Total JD Keywords: {len(jd_keywords)}")
        print(f"Matched Keywords: {len(matched_keywords)}")
        print(f"Missing Keywords: {len(missing_keywords)}")
        print(f"Coverage: {len(matched_keywords)/len(jd_keywords)*100:.1f}%")
        print()
        
        print("Matched Keywords (Present in Resume):")
        for i, keyword in enumerate(matched_keywords, 1):
            print(f"  {i:2d}. {keyword}")
        print()
        
        print("Missing Keywords (Top 10):")
        for i, keyword in enumerate(missing_keywords[:10], 1):
            print(f"  {i:2d}. {keyword}")
        print()
        
        # Test with problematic examples from the requirements
        print("=== Testing Problematic Examples ===")
        problematic_jd = """
        We need someone who can build great products that meet our requirements.
        You will connect with stakeholders and review designs rapidly. The role 
        involves working with tools and services to support our team. You should 
        have experience with ideae and be able to work in a fast-paced environment.
        """
        
        problematic_keywords = extractor.extract_smart_keywords(problematic_jd, 10)
        print("Keywords extracted from problematic JD:")
        for i, keyword in enumerate(problematic_keywords, 1):
            print(f"  {i:2d}. {keyword}")
        print()
        
        # Check if noise was filtered out
        noise_words = ['built', 'meets', 'connects', 'reviews', 'dots', 'points', 'rapidly', 'ideae']
        filtered_noise = [word for word in noise_words if word in problematic_keywords]
        print(f"Noise words that should be filtered: {noise_words}")
        print(f"Noise words still present: {filtered_noise}")
        print(f"✓ Noise filtering: {'PASS' if len(filtered_noise) == 0 else 'FAIL'}")
        print()
        
        print("=== Test Completed Successfully ===")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_smart_keyword_extraction()
    sys.exit(0 if success else 1)
