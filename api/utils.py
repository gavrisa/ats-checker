"""
Advanced keyword extraction utilities for ATS analysis
"""

import re
import math
from typing import List, Tuple, Dict, Set
from collections import Counter, defaultdict

# Enhanced stopwords including new additions
ENHANCED_STOPWORDS = {
    # Original stopwords
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
    'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
    
    # New additions from requirements
    'over', 'give', 'complete', 'control', 'move', 'act', 'person', 'part', 'now', 'where',
    
    # Meaningless fragments
    're', 've', 'll', 'd', 't', 's', 'don', 'won', 'can', 'will',
    
    # Generic business words
    'work', 'team', 'company', 'business', 'role', 'position', 'job', 'opportunity',
    'experience', 'skills', 'knowledge', 'ability', 'responsible', 'responsibilities',
    'requirements', 'required', 'preferred', 'ideal', 'candidate', 'looking', 'seeking',
    'join', 'grow', 'build', 'create', 'develop', 'support', 'help', 'ensure', 'provide',
    'manage', 'lead', 'coordinate', 'collaborate', 'communicate', 'working', 'years',
    
    # HR/Benefits words
    'salary', 'benefits', 'vacation', 'health', 'insurance', '401k', 'bonus', 'equity',
    'remote', 'office', 'flexible', 'hours', 'culture', 'diversity', 'inclusion',
    'equal', 'employer', 'discrimination', 'background', 'check'
}

# Domain-specific terms that should be preserved
DOMAIN_KEYWORDS = {
    'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'indesign',
    'accessibility', 'wcag', 'aria', 'inclusive',
    'prototyping', 'wireframing', 'mockups',
    'user research', 'usability testing', 'user interviews',
    'design system', 'component library', 'design tokens',
    'information architecture', 'user journey', 'user flow',
    'procurement', 'saas solutions', 'b2b', 'enterprise',
    'agile', 'scrum', 'kanban', 'jira', 'confluence',
    'react', 'vue', 'angular', 'javascript', 'typescript',
    'python', 'java', 'sql', 'api', 'rest', 'graphql'
}

# Preferred n-grams that should stay together
NGRAM_PATTERNS = {
    'design system', 'user research', 'user experience', 'user interface',
    'usability testing', 'user interviews', 'user journey', 'user flow',
    'information architecture', 'interaction design', 'visual design',
    'design thinking', 'human centered design', 'service design',
    'component library', 'design tokens', 'style guide',
    'accessibility standards', 'inclusive design', 'wcag compliance',
    'saas solutions', 'procurement platform', 'supplier management',
    'spend analytics', 'data visualization', 'business intelligence',
    'project management', 'product management', 'stakeholder management',
    'cross functional', 'agile methodology', 'design sprint',
    'prototype testing', 'a/b testing', 'conversion optimization'
}

# Lemmatization dictionary for common variations
LEMMATIZATION_MAP = {
    'designs': 'design', 'designing': 'design', 'designed': 'design',
    'interviews': 'interview', 'interviewing': 'interview', 'interviewed': 'interview',
    'tests': 'test', 'testing': 'test', 'tested': 'test',
    'prototypes': 'prototype', 'prototyping': 'prototype',
    'wireframes': 'wireframe', 'wireframing': 'wireframe',
    'researches': 'research', 'researching': 'research', 'researched': 'research',
    'analyses': 'analysis', 'analyzing': 'analysis', 'analyzed': 'analysis',
    'methodologies': 'methodology', 'methods': 'method',
    'technologies': 'technology', 'solutions': 'solution',
    'systems': 'system', 'platforms': 'platform',
    'frameworks': 'framework', 'libraries': 'library',
    'processes': 'process', 'procedures': 'procedure'
}

# Section weights for scoring
SECTION_WEIGHTS = {
    'responsibilities': 1.0,
    'requirements': 0.9,
    'duties': 1.0,
    'qualifications': 0.8,
    'skills': 0.9,
    'experience': 0.8,
    'about': 0.3,
    'company': 0.2,
    'benefits': 0.1,
    'perks': 0.1
}

# Manual boosts for important keywords
KEYWORD_BOOSTS = {
    'figma': 1.5,
    'prototyping': 1.3,
    'accessibility': 1.4,
    'procurement': 1.3,
    'design system': 1.5,
    'user research': 1.4,
    'usability testing': 1.3,
    'wireframing': 1.2,
    'saas': 1.2,
    'agile': 1.1,
    'scrum': 1.1
}

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    # Remove special characters but preserve hyphens and spaces
    text = re.sub(r'[^\w\s\-]', ' ', text.lower())
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def detect_company_names(jd_text: str) -> Set[str]:
    """
    Detect potential company names from job description
    Uses simple heuristics to identify proper nouns that might be company names
    """
    company_names = set()
    
    # Look for patterns like "at CompanyName" or "join CompanyName"
    patterns = [
        r'(?:at|join|for|with)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:is|offers|provides)',
        # Common company suffixes
        r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:Inc|LLC|Corp|Ltd|AS|AB)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, jd_text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            # Filter out common false positives
            if len(match) > 2 and match.lower() not in ENHANCED_STOPWORDS:
                company_names.add(match.lower())
    
    return company_names

def extract_ngrams(text: str, n: int = 2) -> List[str]:
    """Extract n-grams from text"""
    words = text.split()
    ngrams = []
    
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i + n])
        ngrams.append(ngram)
    
    return ngrams

def lemmatize_keyword(keyword: str) -> str:
    """Apply lemmatization to normalize keyword variations"""
    words = keyword.split()
    lemmatized_words = []
    
    for word in words:
        lemmatized_word = LEMMATIZATION_MAP.get(word, word)
        lemmatized_words.append(lemmatized_word)
    
    return ' '.join(lemmatized_words)

def identify_sections(jd_text: str) -> Dict[str, str]:
    """
    Identify different sections in job description for weighted scoring
    """
    sections = {}
    current_section = 'general'
    
    # Section headers to look for
    section_patterns = {
        'responsibilities': r'(?:responsibilities|duties|what you.*do|your role)',
        'requirements': r'(?:requirements|qualifications|what.*need|must have)',
        'skills': r'(?:skills|technical|competencies)',
        'experience': r'(?:experience|background)',
        'about': r'(?:about|company|who we are)',
        'benefits': r'(?:benefits|perks|offer|compensation)'
    }
    
    lines = jd_text.split('\n')
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        section_found = False
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = section_name
                current_content = []
                section_found = True
                break
        
        if not section_found:
            current_content.append(line)
    
    # Save final section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def calculate_keyword_score(keyword: str, frequency: int, total_words: int, 
                          section_weights: Dict[str, float], 
                          max_frequency: int) -> float:
    """
    Calculate score for a keyword based on multiple factors
    """
    # Base TF score (0-1)
    tf_score = frequency / max_frequency if max_frequency > 0 else 0
    
    # Section weight (0-1)
    section_score = max(section_weights.values()) if section_weights else 0.5
    
    # Length bonus for multi-word terms
    word_count = len(keyword.split())
    length_bonus = min(word_count * 0.1, 0.3)
    
    # Domain keyword bonus
    domain_bonus = 0.2 if any(domain in keyword for domain in DOMAIN_KEYWORDS) else 0
    
    # Manual boost
    manual_boost = KEYWORD_BOOSTS.get(keyword, 1.0)
    
    # Calculate final score
    base_score = (tf_score * 0.5 + section_score * 0.3 + length_bonus + domain_bonus) * manual_boost
    
    return min(base_score, 1.0)  # Cap at 1.0

def extract_keywords_with_scores(jd_text: str, top_n: int = 30) -> List[Tuple[str, float]]:
    """
    Extract and score keywords from job description
    
    Args:
        jd_text: Job description text
        top_n: Number of top keywords to return
        
    Returns:
        List of (keyword, score) tuples sorted by score
    """
    if not jd_text or not jd_text.strip():
        return []
    
    # Normalize text
    normalized_text = normalize_text(jd_text)
    
    # Detect company names to filter out
    company_names = detect_company_names(jd_text)
    
    # Identify sections for weighted scoring
    sections = identify_sections(jd_text)
    
    # Extract candidate keywords
    candidates = set()
    
    # Extract single words
    words = normalized_text.split()
    for word in words:
        if (len(word) >= 3 and 
            word not in ENHANCED_STOPWORDS and 
            word not in company_names and
            not word.isdigit()):
            candidates.add(word)
    
    # Only add specific, high-value 2-word phrases (no automatic n-gram generation)
    specific_2word_phrases = [
        "design system", "user research", "user experience", "usability testing",
        "information architecture", "user interface", "interaction design",
        "visual design", "service design", "design thinking", "design sprint",
        "accessibility standards", "design systems", "component library",
        "user journey", "user flow", "wireframes", "prototyping"
    ]
    
    for phrase in specific_2word_phrases:
        if phrase in normalized_text and not any(company in phrase for company in company_names):
            candidates.add(phrase)
    
    # Filter candidates to 1-2 words only before scoring
    clean_candidates = []
    for candidate in candidates:
        words_in_candidate = candidate.split()
        # Only keep 1-2 word candidates
        if len(words_in_candidate) <= 2:
            clean_candidates.append(candidate)
    
    # Calculate frequencies and scores for clean candidates only
    keyword_scores = {}
    word_frequencies = Counter(normalized_text.split())
    max_frequency = max(word_frequencies.values()) if word_frequencies else 1
    
    for candidate in clean_candidates:
        # Apply lemmatization
        normalized_candidate = lemmatize_keyword(candidate)
        
        # Calculate frequency
        if ' ' in candidate:
            # For phrases, count occurrences in text
            frequency = normalized_text.count(candidate)
        else:
            frequency = word_frequencies.get(candidate, 0)
        
        # Calculate section weights for this keyword
        section_weights_for_keyword = {}
        for section_name, section_text in sections.items():
            if candidate in normalize_text(section_text):
                section_weights_for_keyword[section_name] = SECTION_WEIGHTS.get(section_name, 0.5)
        
        # Calculate score
        score = calculate_keyword_score(
            normalized_candidate, 
            frequency, 
            len(words), 
            section_weights_for_keyword, 
            max_frequency
        )
        
        keyword_scores[normalized_candidate] = score
    
    # Sort by score and return top N
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Ultra-clean deduplication: 1-2 words max, no duplicates
    final_keywords = []
    seen_words = set()
    seen_concepts = set()
    
    # Priority single words and 2-word phrases
    priority_terms = [
        "figma", "sketch", "accessibility", "wireframes", "prototyping", 
        "design system", "user research", "usability testing", "agile", "scrum"
    ]
    
    # First: Add priority terms (exact matches only)
    for keyword, score in sorted_keywords:
        if keyword in priority_terms and keyword not in seen_concepts:
            if len(keyword.split()) <= 2:
                final_keywords.append((keyword, score))
                seen_concepts.add(keyword)
                seen_words.update(keyword.split())
    
    # Second: Add other clean 1-2 word terms
    for keyword, score in sorted_keywords:
        if len(final_keywords) >= top_n:
            break
            
        words = keyword.split()
        
        # Only allow 1-2 words maximum
        if len(words) > 2:
            continue
            
        # Skip if already added
        if keyword in seen_concepts:
            continue
            
        # Skip if any word already used
        if any(word in seen_words for word in words):
            continue
            
        # Skip very generic single words
        if len(words) == 1 and len(keyword) < 4:
            continue
            
        # Add the keyword
        final_keywords.append((keyword, score))
        seen_concepts.add(keyword)
        seen_words.update(words)
    
    # Final absolute filter: ensure NO phrase has more than 2 words
    absolutely_clean_keywords = []
    for keyword, score in final_keywords:
        if len(keyword.split()) <= 2:
            absolutely_clean_keywords.append((keyword, score))
    
    return absolutely_clean_keywords[:top_n]

def extract_keywords(jd_text: str, top_n: int = 30) -> List[str]:
    """
    Extract clean list of keywords (strings only) for backward compatibility
    
    Args:
        jd_text: Job description text
        top_n: Number of top keywords to return
        
    Returns:
        List of keyword strings (GUARANTEED 1-2 words only)
    """
    scored_keywords = extract_keywords_with_scores(jd_text, top_n)
    # ABSOLUTE FINAL FILTER: Remove ANY keyword with more than 2 words
    clean_keywords = []
    for keyword, score in scored_keywords:
        if len(keyword.split()) <= 2:
            clean_keywords.append(keyword)
    return clean_keywords[:top_n]

# Example usage and testing
if __name__ == "__main__":
    sample_jd = """
    Senior UX Designer - Telenor
    
    About Telenor:
    Telenor is a leading telecommunications company.
    
    Responsibilities:
    - Conduct user research and usability testing
    - Create wireframes and interactive prototypes using Figma
    - Develop design systems and component libraries
    - Ensure accessibility compliance (WCAG 2.1)
    - Work with procurement teams on SaaS solutions
    
    Requirements:
    - 5+ years of UX design experience
    - Proficiency in Figma, Sketch, and Adobe Creative Suite
    - Strong background in user research methodologies
    - Experience with accessibility standards
    - Knowledge of design systems and prototyping
    
    Benefits:
    - Competitive salary and health insurance
    - Flexible working hours and remote options
    """
    
    print("Scored Keywords:")
    scored = extract_keywords_with_scores(sample_jd)
    for keyword, score in scored[:15]:
        print(f"{keyword}: {score:.3f}")
    
    print("\nClean Keywords:")
    clean = extract_keywords(sample_jd, 15)
    for i, keyword in enumerate(clean, 1):
        print(f"{i}. {keyword}")
