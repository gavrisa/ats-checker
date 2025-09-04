"""
Ultra-clean keyword extractor that GUARANTEES 1-2 words only
"""
import re
from typing import List, Tuple
from collections import Counter

def clean_extract_keywords(text: str, top_n: int = 30) -> List[Tuple[str, float]]:
    """
    Extract ONLY 1-2 word keywords, no exceptions
    """
    if not text or not text.strip():
        return []
    
    # Normalize text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    text = re.sub(r'\s+', ' ', text.strip())
    
    candidates = set()
    words = text.split()
    
    # Add single words (4+ chars, not generic)
    stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    for word in words:
        if len(word) >= 4 and word not in stopwords:
            candidates.add(word)
    
    # Add specific 2-word phrases
    good_2word_phrases = [
        "design system", "user research", "user experience", "usability testing",
        "information architecture", "user interface", "interaction design",
        "visual design", "accessibility compliance", "design thinking"
    ]
    
    for phrase in good_2word_phrases:
        if phrase in text:
            candidates.add(phrase)
    
    # Score and return - ABSOLUTE guarantee of 1-2 words
    scored = []
    for candidate in candidates:
        word_count = len(candidate.split())
        if word_count <= 2:  # ABSOLUTE FILTER
            frequency = text.count(candidate)
            score = frequency / 10.0 if frequency > 0 else 0.1
            scored.append((candidate, min(score, 1.0)))
    
    # Sort by score and return top N
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]

def clean_extract_keywords_simple(text: str, top_n: int = 30) -> List[str]:
    """
    Simple wrapper that returns only keyword strings
    """
    print(f"🔥 CLEAN EXTRACTOR CALLED WITH: {text[:50]}...")
    scored = clean_extract_keywords(text, top_n)
    result = [keyword for keyword, score in scored]
    print(f"🔥 CLEAN EXTRACTOR RETURNING: {result[:3]}")
    return result
