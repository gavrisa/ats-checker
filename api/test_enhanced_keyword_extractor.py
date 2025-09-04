"""
Comprehensive unit tests for the enhanced keyword extractor.
Tests cover: empty JD, short JD, tool names, pluralization, fuzzy matches, and bullet generation quality.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the api directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_keyword_extractor import EnhancedKeywordExtractor
from config import Config

class TestEnhancedKeywordExtractor:
    """Test suite for EnhancedKeywordExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create an EnhancedKeywordExtractor instance for testing."""
        return EnhancedKeywordExtractor()
    
    @pytest.fixture
    def sample_jd(self):
        """Sample job description for testing."""
        return """
        We are looking for a Senior UX/UI Designer with experience in product design and user research.
        Must have skills in Adobe Creative Suite, HTML/CSS, and JavaScript.
        Experience with Figma, prototyping, and user testing is required.
        """
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume text for testing."""
        return """
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
    
    def test_empty_job_description(self, extractor):
        """Test handling of empty job description."""
        keywords = extractor.extract_enhanced_keywords("")
        assert keywords == []
        
        keywords = extractor.extract_enhanced_keywords("   ")
        assert keywords == []
        
        keywords = extractor.extract_enhanced_keywords(None)
        assert keywords == []
    
    def test_short_job_description(self, extractor):
        """Test handling of very short job description."""
        short_jd = "UX Designer"
        keywords = extractor.extract_enhanced_keywords(short_jd)
        assert len(keywords) > 0
        assert "ux" in [kw.lower() for kw in keywords]
        assert "designer" in [kw.lower() for kw in keywords]
    
    def test_tool_names_extraction(self, extractor, sample_jd):
        """Test that tool names are properly extracted and ranked."""
        keywords = extractor.extract_enhanced_keywords(sample_jd)
        
        # Check that important tools are extracted
        tool_keywords = [kw.lower() for kw in keywords]
        assert "figma" in tool_keywords
        assert "adobe" in tool_keywords or "creative" in tool_keywords
        assert "html" in tool_keywords
        assert "css" in tool_keywords
        assert "javascript" in tool_keywords
    
    def test_pluralization_handling(self, extractor):
        """Test that pluralization is handled correctly."""
        jd_with_plurals = "We need designers with skills in prototypes, wireframes, and user interfaces."
        keywords = extractor.extract_tokens_and_phrases(jd_with_plurals)
        
        # Should extract both singular and plural forms
        assert "designers" in keywords or "designer" in keywords
        assert "prototypes" in keywords or "prototype" in keywords
        assert "wireframes" in keywords or "wireframe" in keywords
    
    def test_fuzzy_matching(self, extractor, sample_jd, sample_resume):
        """Test fuzzy matching functionality."""
        keywords = extractor.extract_enhanced_keywords(sample_jd)
        matched, missing = extractor.find_matching_keywords_fuzzy(sample_resume, keywords)
        
        # Should find matches for key terms
        assert len(matched) > 0
        assert "figma" in [kw.lower() for kw in matched]
        assert "ux" in [kw.lower() for kw in matched] or "ui" in [kw.lower() for kw in matched]
        
        # Missing keywords should be a subset of all keywords
        assert len(missing) <= len(keywords)
        assert all(kw in keywords for kw in missing)
    
    def test_bullet_generation_quality(self, extractor):
        """Test bullet suggestion generation quality."""
        missing_keywords = ["machine learning", "python", "data analysis", "agile"]
        bullets = extractor.generate_enhanced_bullet_suggestions(missing_keywords, 4)
        
        # Should generate the requested number of bullets
        assert len(bullets) == 4
        
        # Each bullet should contain the corresponding keyword
        for i, keyword in enumerate(missing_keywords):
            assert keyword.lower() in bullets[i].lower()
        
        # Bullets should be diverse (no exact duplicates)
        assert len(set(bullets)) == len(bullets)
        
        # Bullets should contain action verbs
        action_verbs = ["led", "designed", "developed", "created", "built", "implemented", "optimized"]
        for bullet in bullets:
            assert any(verb in bullet.lower() for verb in action_verbs)
    
    def test_no_duplicate_verbs(self, extractor):
        """Test that bullet suggestions don't repeat the same verb."""
        missing_keywords = ["python", "javascript", "react", "node.js", "mongodb", "docker"]
        bullets = extractor.generate_enhanced_bullet_suggestions(missing_keywords, 6)
        
        # Extract verbs from bullets (first word after action verb)
        verbs = []
        for bullet in bullets:
            words = bullet.split()
            if len(words) > 0:
                verbs.append(words[0].lower())
        
        # Should have diverse verbs
        assert len(set(verbs)) > 1  # At least 2 different verbs
    
    def test_tfidf_scoring(self, extractor, sample_jd):
        """Test TF-IDF scoring functionality."""
        tokens = extractor.extract_tokens_and_phrases(sample_jd)
        filtered_tokens = extractor.apply_quality_filters(tokens)
        scores = extractor.calculate_tfidf_scores(filtered_tokens, sample_jd)
        
        # Should return scored tokens
        assert len(scores) > 0
        assert all(isinstance(score, tuple) and len(score) == 2 for score in scores)
        assert all(isinstance(score[1], (int, float)) for score in scores)
        
        # Scores should be sorted in descending order
        score_values = [score[1] for score in scores]
        assert score_values == sorted(score_values, reverse=True)
    
    def test_quality_filters(self, extractor):
        """Test quality filtering functionality."""
        # Test with mixed quality tokens
        tokens = ["figma", "the", "ux", "design", "a", "user", "experience", "and", "python"]
        filtered = extractor.apply_quality_filters(tokens)
        
        # Should filter out stop words
        assert "the" not in filtered
        assert "a" not in filtered
        assert "and" not in filtered
        
        # Should keep meaningful terms
        assert "figma" in filtered
        assert "ux" in filtered
        assert "design" in filtered
        assert "user" in filtered
        assert "experience" in filtered
        assert "python" in filtered
    
    def test_ranking_boosts(self, extractor, sample_jd):
        """Test ranking boost functionality."""
        tokens = extractor.extract_tokens_and_phrases(sample_jd)
        filtered_tokens = extractor.apply_quality_filters(tokens)
        scores = extractor.calculate_tfidf_scores(filtered_tokens, sample_jd)
        boosted_scores = extractor.apply_ranking_boosts(scores, sample_jd)
        
        # Should have boosted scores
        assert len(boosted_scores) == len(scores)
        
        # Tool names should be boosted
        tool_scores = {kw: score for kw, score in boosted_scores if kw.lower() in extractor.tool_names}
        if tool_scores:
            # Tool scores should be higher than non-tool scores
            non_tool_scores = {kw: score for kw, score in boosted_scores if kw.lower() not in extractor.tool_names}
            if non_tool_scores:
                avg_tool_score = sum(tool_scores.values()) / len(tool_scores)
                avg_non_tool_score = sum(non_tool_scores.values()) / len(non_tool_scores)
                assert avg_tool_score >= avg_non_tool_score
    
    def test_lemma_deduplication(self, extractor):
        """Test lemma-based deduplication."""
        # Create tokens with different forms of the same word
        token_scores = [
            ("designer", 5.0),
            ("designers", 4.0),
            ("designing", 3.0),
            ("figma", 6.0),
            ("python", 7.0)
        ]
        
        deduplicated = extractor.deduplicate_by_lemma(token_scores)
        
        # Should reduce duplicates
        assert len(deduplicated) <= len(token_scores)
        
        # Should keep the highest scoring form
        designer_forms = [kw for kw, score in deduplicated if "design" in kw.lower()]
        assert len(designer_forms) <= 1  # Should deduplicate designer/designers/designing
    
    def test_enhanced_scores_calculation(self, extractor, sample_jd, sample_resume):
        """Test enhanced score calculation."""
        keywords = extractor.extract_enhanced_keywords(sample_jd)
        matched, missing = extractor.find_matching_keywords_fuzzy(sample_resume, keywords)
        scores = extractor.calculate_enhanced_scores(matched, keywords, sample_resume, sample_jd)
        
        # Should return valid scores
        assert "score" in scores
        assert "similarity" in scores
        assert "coverage" in scores
        
        # Scores should be in valid ranges
        assert 0 <= scores["score"] <= 100
        assert 0 <= scores["similarity"] <= 100
        assert 0 <= scores["coverage"] <= 100
        
        # Coverage should be calculated correctly
        expected_coverage = len(matched) / max(len(keywords), 1) * 100
        assert abs(scores["coverage"] - expected_coverage) < 0.1
    
    def test_edge_case_empty_keywords(self, extractor, sample_resume):
        """Test edge case with empty keywords list."""
        matched, missing = extractor.find_matching_keywords_fuzzy(sample_resume, [])
        assert matched == []
        assert missing == []
        
        scores = extractor.calculate_enhanced_scores([], [], sample_resume, "")
        assert scores["score"] == 0
        assert scores["similarity"] == 0
        assert scores["coverage"] == 0
    
    def test_edge_case_no_matches(self, extractor, sample_jd):
        """Test edge case with no keyword matches."""
        resume_with_no_matches = "Completely unrelated content about cooking and gardening."
        keywords = extractor.extract_enhanced_keywords(sample_jd)
        matched, missing = extractor.find_matching_keywords_fuzzy(resume_with_no_matches, keywords)
        
        assert matched == []
        assert missing == keywords
        
        scores = extractor.calculate_enhanced_scores(matched, keywords, resume_with_no_matches, sample_jd)
        assert scores["coverage"] == 0
    
    def test_meaningful_phrase_detection(self, extractor):
        """Test meaningful phrase detection."""
        # Test meaningful phrases
        assert extractor._is_meaningful_phrase("user experience") == True
        assert extractor._is_meaningful_phrase("data analysis") == True
        assert extractor._is_meaningful_phrase("machine learning") == True
        
        # Test non-meaningful phrases
        assert extractor._is_meaningful_phrase("we are") == False
        assert extractor._is_meaningful_phrase("for the") == False
        assert extractor._is_meaningful_phrase("in the") == False
    
    def test_skill_detection(self, extractor):
        """Test skill detection functionality."""
        # Test tech patterns
        assert extractor._looks_like_skill("API") == True
        assert extractor._looks_like_skill("React.js") == True
        assert extractor._looks_like_skill("Python") == True
        
        # Test skill patterns
        assert extractor._looks_like_skill("web development") == True
        assert extractor._looks_like_skill("software engineering") == True
        
        # Test non-skills
        assert extractor._looks_like_skill("the") == False
        assert extractor._looks_like_skill("and") == False
    
    def test_config_integration(self):
        """Test configuration integration."""
        config = Config()
        
        # Test feature flags
        assert isinstance(config.SEMANTIC_ON, bool)
        assert isinstance(config.PY_SIDECAR_ON, bool)
        
        # Test configuration values
        assert config.MAX_KEYWORDS > 0
        assert config.MAX_MISSING_KEYWORDS > 0
        assert config.MAX_BULLET_SUGGESTIONS > 0
        
        # Test dictionary conversion
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "semantic_on" in config_dict
        assert "max_keywords" in config_dict
        
        # Test feature flags
        feature_flags = config.get_feature_flags()
        assert isinstance(feature_flags, dict)
        assert "enhanced_keywords" in feature_flags
        assert "fuzzy_matching" in feature_flags

class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test the complete keyword extraction and matching workflow."""
        extractor = EnhancedKeywordExtractor()
        
        jd = """
        Senior Software Engineer
        We are looking for a Senior Software Engineer with experience in Python, JavaScript, and React.
        Must have experience with AWS, Docker, and agile development.
        Experience with machine learning and data analysis is a plus.
        """
        
        resume = """
        John Doe
        Senior Software Engineer
        
        Experience:
        - Developed web applications using Python and JavaScript
        - Built React components and managed state
        - Deployed applications on AWS using Docker
        - Led agile development processes
        - Implemented machine learning models for data analysis
        
        Skills: Python, JavaScript, React, AWS, Docker, Agile, Machine Learning
        """
        
        # Extract keywords
        keywords = extractor.extract_enhanced_keywords(jd)
        assert len(keywords) > 0
        
        # Find matches
        matched, missing = extractor.find_matching_keywords_fuzzy(resume, keywords)
        assert len(matched) > 0
        assert len(missing) < len(keywords)
        
        # Calculate scores
        scores = extractor.calculate_enhanced_scores(matched, keywords, resume, jd)
        assert scores["score"] > 0
        assert scores["coverage"] > 0
        
        # Generate bullet suggestions
        bullets = extractor.generate_enhanced_bullet_suggestions(missing, 5)
        assert len(bullets) > 0
        assert len(bullets) <= 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

