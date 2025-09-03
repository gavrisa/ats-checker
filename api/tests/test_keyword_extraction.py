"""
Tests for keyword extraction functions
"""
import pytest
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    extract_ats_keywords, 
    match_keywords_to_cv, 
    generate_bullet_suggestions,
    normalize_text,
    extract_phrases,
    is_generic_word,
    is_whitelisted_single,
    is_preferred_pattern,
    calculate_phrase_score,
    deduplicate_phrases,
    get_debug_info
)

class TestNormalizeText:
    """Test text normalization function"""
    
    def test_normalize_text_basic(self):
        """Test basic text normalization"""
        input_text = "Hello, World! This is a TEST."
        expected = "hello  world  this is a test "
        result = normalize_text(input_text)
        assert result == expected
    
    def test_normalize_text_special_chars(self):
        """Test normalization with special characters"""
        input_text = "User@Experience & Design#123"
        expected = "user experience   design 123"
        result = normalize_text(input_text)
        assert result == expected
    
    def test_normalize_text_empty(self):
        """Test normalization with empty string"""
        result = normalize_text("")
        assert result == ""

class TestExtractPhrases:
    """Test phrase extraction function"""
    
    def test_extract_phrases_basic(self):
        """Test basic phrase extraction"""
        text = "user experience design"
        phrases = extract_phrases(text, max_length=3)
        expected_phrases = [
            "user experience", "experience design",  # 2-word phrases
            "user experience design"  # 3-word phrase
        ]
        assert all(phrase in phrases for phrase in expected_phrases)
    
    def test_extract_phrases_limit(self):
        """Test phrase extraction with limits"""
        text = "word " * 100  # 100 words
        phrases = extract_phrases(text, max_length=2)
        # Should limit to prevent timeout
        assert len(phrases) <= 5000
    
    def test_extract_phrases_empty(self):
        """Test phrase extraction with empty text"""
        phrases = extract_phrases("")
        assert phrases == []

class TestGenericWordFiltering:
    """Test generic word filtering functions"""
    
    def test_is_generic_word(self):
        """Test generic word detection"""
        assert is_generic_word("the") == True
        assert is_generic_word("and") == True
        assert is_generic_word("experience") == True
        assert is_generic_word("python") == False
        assert is_generic_word("accessibility") == False
    
    def test_is_whitelisted_single(self):
        """Test whitelisted single word detection"""
        assert is_whitelisted_single("accessibility") == True
        assert is_whitelisted_single("personas") == True
        assert is_whitelisted_single("wireframes") == True
        assert is_whitelisted_single("random") == False
    
    def test_is_preferred_pattern(self):
        """Test preferred pattern detection"""
        assert is_preferred_pattern("user research") == True
        assert is_preferred_pattern("usability testing") == True
        assert is_preferred_pattern("random phrase") == False

class TestKeywordExtraction:
    """Test main keyword extraction function"""
    
    def test_extract_ats_keywords_basic(self, sample_jd):
        """Test basic keyword extraction"""
        keywords = extract_ats_keywords(sample_jd)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert len(keywords) <= 30
        
        # Should contain domain-specific terms
        keyword_text = " ".join(keywords).lower()
        assert any(term in keyword_text for term in ["research", "usability", "wireframe", "accessibility"])
    
    def test_extract_ats_keywords_empty(self):
        """Test keyword extraction with empty text"""
        keywords = extract_ats_keywords("")
        assert keywords == []
    
    def test_extract_ats_keywords_short_text(self):
        """Test keyword extraction with very short text"""
        short_text = "UX Designer position"
        keywords = extract_ats_keywords(short_text)
        assert isinstance(keywords, list)
    
    def test_extract_ats_keywords_filters_generic(self):
        """Test that generic words are filtered out"""
        text = "Python developer will work with the team to develop software solutions"
        keywords = extract_ats_keywords(text)
        
        # Should contain meaningful keywords but not generic words
        assert len(keywords) > 0
        # Should not contain standalone generic words
        generic_words = ["the", "will", "work", "with", "team", "to", "and", "or"]
        for keyword in keywords:
            assert keyword.lower() not in generic_words

class TestKeywordMatching:
    """Test keyword matching against CV"""
    
    def test_match_keywords_to_cv_basic(self, sample_cv):
        """Test basic keyword matching"""
        jd_keywords = ["user research", "wireframes", "accessibility", "python", "missing keyword"]
        result = match_keywords_to_cv(jd_keywords, sample_cv)
        
        assert "matched_keywords" in result
        assert "missing_keywords" in result
        assert isinstance(result["matched_keywords"], list)
        assert isinstance(result["missing_keywords"], list)
        
        # Should match existing keywords
        assert "user research" in result["matched_keywords"]
        assert "wireframes" in result["matched_keywords"]
        assert "accessibility" in result["matched_keywords"]
        
        # Should identify missing keywords
        assert "python" in result["missing_keywords"]
        assert "missing keyword" in result["missing_keywords"]
    
    def test_match_keywords_empty_cv(self):
        """Test keyword matching with empty CV"""
        jd_keywords = ["user research", "wireframes"]
        result = match_keywords_to_cv(jd_keywords, "")
        
        assert len(result["matched_keywords"]) == 0
        assert len(result["missing_keywords"]) == len(jd_keywords)
    
    def test_match_keywords_empty_list(self, sample_cv):
        """Test keyword matching with empty keyword list"""
        result = match_keywords_to_cv([], sample_cv)
        
        assert result["matched_keywords"] == []
        assert result["missing_keywords"] == []

class TestBulletSuggestions:
    """Test bullet suggestion generation"""
    
    def test_generate_bullet_suggestions_basic(self):
        """Test basic bullet suggestion generation"""
        missing_keywords = ["user research", "accessibility", "wireframes"]
        suggestions = generate_bullet_suggestions(missing_keywords)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) >= 3
        assert len(suggestions) <= 5
        
        # Each suggestion should be a string
        assert all(isinstance(s, str) for s in suggestions)
        
        # Suggestions should contain the keywords
        suggestion_text = " ".join(suggestions).lower()
        assert any(keyword.lower() in suggestion_text for keyword in missing_keywords)
    
    def test_generate_bullet_suggestions_empty(self):
        """Test bullet suggestion generation with empty list"""
        suggestions = generate_bullet_suggestions([])
        
        assert isinstance(suggestions, list)
        assert len(suggestions) >= 4  # Should provide generic suggestions
    
    def test_generate_bullet_suggestions_word_limit(self):
        """Test that suggestions respect word limit"""
        missing_keywords = ["very long keyword phrase that might exceed limits"]
        suggestions = generate_bullet_suggestions(missing_keywords)
        
        # Each suggestion should be <= 20 words
        for suggestion in suggestions:
            word_count = len(suggestion.split())
            assert word_count <= 20

class TestPhraseScoring:
    """Test phrase scoring function"""
    
    def test_calculate_phrase_score(self):
        """Test phrase score calculation"""
        text = "user research is important for user experience design user research"
        phrase = "user research"
        
        score = calculate_phrase_score(phrase, text, {})
        
        assert isinstance(score, float)
        assert score >= 0.0
        assert score <= 1.0
    
    def test_calculate_phrase_score_preferred_pattern(self):
        """Test that preferred patterns get higher scores"""
        text = "user research and random phrase"
        
        preferred_score = calculate_phrase_score("user research", text, {})
        regular_score = calculate_phrase_score("random phrase", text, {})
        
        assert preferred_score > regular_score

class TestDeduplication:
    """Test phrase deduplication"""
    
    def test_deduplicate_phrases_basic(self):
        """Test basic phrase deduplication"""
        phrases = ["user journey", "customer journey", "wireframe", "wireframes"]
        deduplicated = deduplicate_phrases(phrases)
        
        # Should reduce similar phrases
        assert len(deduplicated) <= len(phrases)
        
        # Should keep the first occurrence from synonym groups
        assert "user journey" in deduplicated
        assert "wireframe" in deduplicated

class TestDebugInfo:
    """Test debug information function"""
    
    def test_get_debug_info(self, sample_jd):
        """Test debug information generation"""
        debug_info = get_debug_info(sample_jd)
        
        assert "dropped_examples" in debug_info
        assert "kept_examples" in debug_info
        assert isinstance(debug_info["dropped_examples"], list)
        assert isinstance(debug_info["kept_examples"], list)
        
        # Should have some examples
        assert len(debug_info["dropped_examples"]) > 0
        assert len(debug_info["kept_examples"]) > 0
