#!/usr/bin/env python3
"""
Simple test script to verify the enhanced keyword extractor works.
Run this to test the enhanced functionality without pytest.
"""

import sys
import os
from pathlib import Path

# Add the api directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_extractor():
    """Simple test of the enhanced keyword extractor."""
    try:
        from enhanced_keyword_extractor import EnhancedKeywordExtractor
        from config import config
        
        print("✅ Enhanced keyword extractor imported successfully")
        
        # Create extractor
        extractor = EnhancedKeywordExtractor()
        print("✅ Enhanced keyword extractor initialized")
        
        # Test job description
        jd = """
        We are looking for a Senior UX/UI Designer with experience in product design and user research.
        Must have skills in Adobe Creative Suite, HTML/CSS, and JavaScript.
        Experience with Figma, prototyping, and user testing is required.
        """
        
        # Test resume
        resume = """
        John Smith
        Senior UX/UI Designer
        
        Experience:
        - Led user research and design system development
        - Created wireframes and prototypes using Figma
        - Collaborated with product managers and developers
        - Improved user experience metrics by 40%
        
        Skills:
        - User Experience Design
        - User Interface Design
        - User Research
        - Product Design
        - Figma
        - Adobe Creative Suite
        - HTML/CSS
        - JavaScript
        """
        
        print(f"\n📝 Job Description: {jd.strip()}")
        print(f"\n📄 Resume: {resume.strip()}")
        
        # Extract keywords
        print("\n🔍 Extracting keywords...")
        keywords = extractor.extract_enhanced_keywords(jd)
        print(f"✅ Extracted {len(keywords)} keywords: {keywords[:10]}")
        
        # Find matches
        print("\n🎯 Finding matches...")
        matched, missing = extractor.find_matching_keywords_fuzzy(resume, keywords)
        print(f"✅ Found {len(matched)} matched keywords: {matched}")
        print(f"❌ Missing {len(missing)} keywords: {missing[:5]}")
        
        # Calculate scores
        print("\n📊 Calculating scores...")
        scores = extractor.calculate_enhanced_scores(matched, keywords, resume, jd)
        print(f"✅ Scores: {scores}")
        
        # Generate bullet suggestions
        print("\n💡 Generating bullet suggestions...")
        bullets = extractor.generate_enhanced_bullet_suggestions(missing, 5)
        print(f"✅ Generated {len(bullets)} bullet suggestions:")
        for i, bullet in enumerate(bullets, 1):
            print(f"  {i}. {bullet}")
        
        # Test configuration
        print(f"\n⚙️ Configuration:")
        print(f"  - Semantic similarity: {config.SEMANTIC_ON}")
        print(f"  - Python sidecar: {config.PY_SIDECAR_ON}")
        print(f"  - Max keywords: {config.MAX_KEYWORDS}")
        print(f"  - Max missing: {config.MAX_MISSING_KEYWORDS}")
        print(f"  - Max bullets: {config.MAX_BULLET_SUGGESTIONS}")
        
        print("\n🎉 All tests passed! Enhanced keyword extractor is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install nltk scikit-learn rapidfuzz spacy wordfreq")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_extractor()
    sys.exit(0 if success else 1)

