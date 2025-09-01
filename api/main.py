from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import re
import random
from typing import List, Set, Dict, Any
import json

app = FastAPI(title="ATS Resume Checker", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generic stopwords to exclude (as per HARD FILTERS)
GENERIC_STOPWORDS = {
    # Original list
    'internal', 'key', 'points', 'total', 'experience', 'visual', 'designers', 'language',
    'values', 'data', 'cross', 'remote', 'dependent', 'competitive', 'functional',
    'innovation', 'components', 'interaction', 'designing', 'factors', 'portfolio', 'scalability',
    'communication', 'collaboration', 'usability', 'stakeholders',
    
    # Common stopwords that should always be excluded
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
    'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn',
    'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn',
    
    # Generic business words
    'work', 'team', 'product', 'system', 'who', 'lead', 'global', 'pay', 'our', 'you', 'are', 'that', 'will', 'this',
    'norma', 'help', 'manage', 'encourage', 'part', 'designer', 'culture', 'around', 'world',
    
    # Generic action words
    'get', 'go', 'come', 'make', 'take', 'give', 'find', 'see', 'know', 'think', 'feel', 'say', 'tell', 'ask',
    'call', 'try', 'use', 'want', 'need', 'like', 'love', 'hate', 'good', 'bad', 'big', 'small', 'new', 'old',
    'high', 'low', 'long', 'short', 'right', 'left', 'first', 'last', 'next', 'previous', 'current', 'former',
    
    # Generic descriptive words
    'great', 'good', 'bad', 'better', 'worse', 'best', 'worst', 'important', 'necessary', 'essential', 'critical',
    'major', 'minor', 'primary', 'secondary', 'main', 'basic', 'simple', 'complex', 'easy', 'hard', 'difficult',
    'possible', 'impossible', 'likely', 'unlikely', 'certain', 'uncertain', 'clear', 'unclear', 'obvious', 'hidden',
    
    # Generic time words
    'today', 'yesterday', 'tomorrow', 'now', 'then', 'when', 'while', 'during', 'before', 'after', 'since', 'until',
    'always', 'never', 'sometimes', 'often', 'rarely', 'usually', 'normally', 'typically', 'generally', 'usually',
    
    # Generic location words
    'here', 'there', 'where', 'everywhere', 'nowhere', 'somewhere', 'anywhere', 'inside', 'outside', 'above', 'below',
    'near', 'far', 'close', 'distant', 'local', 'global', 'national', 'international', 'worldwide', 'around', 'across',
    
    # Generic quantity words
    'all', 'some', 'any', 'none', 'many', 'few', 'several', 'various', 'different', 'same', 'similar', 'other', 'another',
    'each', 'every', 'both', 'either', 'neither', 'one', 'two', 'three', 'first', 'second', 'third', 'last', 'next',
    
    # Generic job posting words
    'looking', 'seeking', 'hiring', 'recruiting', 'searching', 'finding', 'identifying', 'selecting', 'choosing',
    'picking', 'deciding', 'determining', 'establishing', 'setting', 'defining', 'describing', 'explaining',
    'clarifying', 'specifying', 'detailing', 'outlining', 'summarizing', 'reviewing', 'evaluating', 'assessing',
    'analyzing', 'examining', 'investigating', 'studying', 'researching', 'exploring', 'discovering', 'learning',
    'understanding', 'knowing', 'recognizing', 'realizing', 'seeing', 'noticing', 'observing', 'watching',
    'monitoring', 'tracking', 'following', 'pursuing', 'chasing', 'seeking', 'looking', 'using', 'utilizing',
    'applying', 'employing', 'leveraging', 'taking', 'making', 'doing', 'getting', 'having', 'being', 'becoming',
    'turning', 'going', 'coming', 'moving', 'changing', 'improving', 'getting', 'becoming', 'turning',
    
    # Additional trash words from the image
    'responsibilities', 'ability', 'organisation', 'experiences', 'recruit', 'impact', 'enable', 'collaborate', 'remoters',
    'contribute', 'nearby', 'saas solutions', 'develop', 'support', 'effective', 'employment', 'business', 'candidates',
    'yourself', 'improve', 'future', 'ambitious', 'cross-functional', 'documentation', 'materials', 'skills',
    'systems', 'organisation', 'organisation', 'organisation', 'organisation', 'organisation', 'organisation',
    
    # More generic words
    'create', 'implement', 'enhance', 'platform', 'understand', 'evaluation', 'optimize', 'solutions', 'research',
    'conduct', 'create', 'implement', 'enhance', 'platform', 'understand', 'evaluation', 'optimize', 'solutions',
    'feedback', 'responsibilities', 'conduct', 'create', 'implement', 'enhance', 'platform', 'understand',
    'evaluation', 'optimize', 'solutions', 'research', 'conduct', 'create', 'implement', 'enhance', 'platform',
    'understand', 'evaluation', 'optimize', 'solutions', 'feedback', 'responsibilities', 'conduct', 'create',
    'implement', 'enhance', 'platform', 'understand', 'evaluation', 'optimize', 'solutions', 'research', 'conduct',
    'create', 'implement', 'enhance', 'platform', 'understand', 'evaluation', 'optimize', 'solutions', 'feedback'
}

# Whitelist for single tokens (allow as single tokens if present in JD)
WHITELIST_SINGLE = {
    'accessibility', 'personas', 'wireframes', 'prototypes', 'heuristics', 'typography', 'a/b testing',
    'ethnography', 'facilitation', 'triangulation', 'analytics', 'mixed-methods'
}

# Preferred multiword patterns (examples; keep if present/derivable)
PREFERRED_PATTERNS = {
    'user research', 'qualitative research', 'quantitative research', 'mixed-methods research',
    'usability testing', 'heuristic evaluation',
    'personas', 'user journeys', 'experience maps', 'task flows', 'interaction models',
    'wireframes', 'interactive prototypes', 'design documentation',
    'information architecture', 'content strategy',
    'accessibility', 'wcag', 'inclusive design',
    'discovery phase', 'problem framing', 'insights synthesis',
    'stakeholder alignment', 'internal stakeholders', 'external stakeholders',
    'product development teams', 'cross-functional collaboration',
    'design system', 'component library', 'tokens',
    'complex saas', 'saas solutions', 'procurement platform', 'supplier intelligence', 'spend analytics',
    'a/b testing', 'survey design', 'interview guides', 'research ops',
    'service blueprint', 'journey analytics'
}

# Synonym groups for deduplication
SYNONYM_GROUPS = {
    'user journey': ['customer journey', 'user journey'],
    'prototype': ['prototyping', 'prototype'],
    'persona': ['personas', 'persona'],
    'wireframe': ['wireframes', 'wireframe'],
    'usability test': ['usability testing', 'usability test'],
    'qualitative': ['qualitative research', 'qualitative'],
    'quantitative': ['quantitative research', 'quantitative']
}

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    return re.sub(r'[^\w\s-]', ' ', text.lower())

def extract_phrases(text: str, max_length: int = 4) -> List[str]:
    """Extract phrases of 2-4 words from text"""
    words = text.split()
    phrases = []
    
    # Limit the number of phrases to prevent timeout
    max_phrases = 1000
    
    for length in range(2, max_length + 1):
        for i in range(len(words) - length + 1):
            if len(phrases) >= max_phrases:
                break
            phrase = ' '.join(words[i:i + length])
            phrases.append(phrase)
        if len(phrases) >= max_phrases:
            break
    
    return phrases

def is_generic_word(word: str) -> bool:
    """Check if word is generic and should be excluded"""
    return word in GENERIC_STOPWORDS

def is_whitelisted_single(word: str) -> bool:
    """Check if word is on the whitelist for single tokens"""
    return word in WHITELIST_SINGLE

def is_preferred_pattern(phrase: str) -> bool:
    """Check if phrase matches preferred multiword patterns"""
    return phrase in PREFERRED_PATTERNS

def calculate_phrase_score(phrase: str, text: str, section_weights: Dict[str, float]) -> float:
    """Calculate score for a phrase based on TF, section proximity, and specificity"""
    words = text.split()
    phrase_words = phrase.split()
    
    # TF weight (0.45)
    tf_weight = 0.45
    phrase_count = text.count(phrase)
    tf_score = min(phrase_count / 10.0, 1.0) * tf_weight
    
    # Section proximity weight (0.30)
    section_weight = 0.30
    section_score = 0.0
    section_keywords = ['responsibilities', 'requirements', 'what you\'ll do', 'key duties', 'essential functions']
    
    # Find if phrase appears near section keywords
    for i, word in enumerate(words):
        for section_keyword in section_keywords:
            if section_keyword in ' '.join(words[max(0, i-5):i+6]):
                if phrase in ' '.join(words[max(0, i-10):i+11]):
                    section_score = section_weight
                    break
    
    # Specificity weight (0.25)
    specificity_weight = 0.25
    specificity_score = 0.0
    
    # Multiword phrases get higher specificity
    if len(phrase_words) > 1:
        specificity_score += 0.1
    
    # Preferred pattern match gets higher specificity
    if is_preferred_pattern(phrase):
        specificity_score += 0.15
    
    specificity_score = min(specificity_score, specificity_weight)
    
    return tf_score + section_score + specificity_score

def deduplicate_phrases(phrases: List[str]) -> List[str]:
    """Deduplicate phrases using synonym collapsing"""
    # Group phrases by their base form
    phrase_groups = {}
    
    for phrase in phrases:
        base_phrase = None
        
        # Check if phrase is in any synonym group
        for base, synonyms in SYNONYM_GROUPS.items():
            if phrase in synonyms:
                base_phrase = base
                break
        
        if base_phrase:
            if base_phrase not in phrase_groups:
                phrase_groups[base_phrase] = []
            phrase_groups[base_phrase].append(phrase)
        else:
            # Use phrase as its own base
            if phrase not in phrase_groups:
                phrase_groups[phrase] = [phrase]
    
    # Pick the most representative phrase from each group
    deduplicated = []
    for base, group in phrase_groups.items():
        # Prefer the JD's wording (first occurrence)
        deduplicated.append(group[0])
    
    return deduplicated

def extract_ats_keywords(jd_text: str) -> List[str]:
    """Extract ATS keywords from job description following the specified rules"""
    normalized_text = normalize_text(jd_text)
    
    # Extract single words and phrases (limit to prevent timeout)
    words = normalized_text.split()[:1000]  # Limit words to prevent timeout
    phrases = extract_phrases(normalized_text)[:500]  # Limit phrases to prevent timeout
    
    candidates = []
    
    # Process single words - MUCH MORE AGGRESSIVE FILTERING
    for word in words:
        if len(word) < 4:  # Increased minimum length
            continue
        
        # Skip generic words unless they are whitelisted
        if is_generic_word(word) and not is_whitelisted_single(word):
            continue
        
        # Skip verbs/adjectives alone
        if word.endswith(('ing', 'ed', 'ly', 'er', 'est')):
            continue
        
        # Skip common short words
        if len(word) <= 4 and word not in WHITELIST_SINGLE:
            continue
        
        # Only add if it's a meaningful technical term or on whitelist
        if is_whitelisted_single(word) or len(word) >= 6 or is_preferred_pattern(word):
            candidates.append(word)
    
    # Process phrases - PRIORITIZE DOMAIN-SPECIFIC PHRASES
    for phrase in phrases:
        phrase_words = phrase.split()
        
        # Skip if any word in phrase is generic (unless it forms a meaningful phrase)
        if any(is_generic_word(word) for word in phrase_words) and not is_preferred_pattern(phrase):
            continue
        
        # Skip if phrase is just verbs/adjectives
        if all(word.endswith(('ing', 'ed', 'ly')) for word in phrase_words):
            continue
        
        # Skip very short phrases unless they're preferred patterns
        if len(phrase_words) == 2 and not is_preferred_pattern(phrase):
            continue
        
        # Prioritize domain-specific phrases
        if is_preferred_pattern(phrase):
            candidates.insert(0, phrase)  # Add to beginning for higher priority
        else:
            candidates.append(phrase)
    
    # Calculate scores for all candidates (limit to prevent timeout)
    scored_candidates = []
    for candidate in candidates[:200]:  # Limit candidates to prevent timeout
        score = calculate_phrase_score(candidate, normalized_text, {})
        scored_candidates.append((candidate, score))
    
    # Sort by score (descending) and break ties by length/specificity
    scored_candidates.sort(key=lambda x: (x[1], len(x[0].split()), is_preferred_pattern(x[0])), reverse=True)
    
    # Deduplicate
    unique_candidates = deduplicate_phrases([c[0] for c in scored_candidates])
    
    # Return top 30, but only if they're meaningful
    meaningful_candidates = []
    for candidate in unique_candidates:
        if is_preferred_pattern(candidate) or len(candidate.split()) >= 2 or len(candidate) >= 6:
            meaningful_candidates.append(candidate)
        if len(meaningful_candidates) >= 30:
            break
    
    return meaningful_candidates[:30]

def match_keywords_to_cv(jd_keywords: List[str], cv_text: str) -> Dict[str, List[str]]:
    """Match JD keywords against CV text with improved matching"""
    normalized_cv = normalize_text(cv_text)
    
    matched = []
    missing = []
    
    for keyword in jd_keywords:
        # Check for exact match
        if keyword in normalized_cv:
            matched.append(keyword)
            continue
        
        # Check for word-by-word match (for multi-word phrases)
        keyword_words = keyword.split()
        if len(keyword_words) > 1:
            # Check if all words in the keyword appear in the CV
            all_words_found = True
            for word in keyword_words:
                if word not in normalized_cv:
                    all_words_found = False
                    break
            if all_words_found:
                matched.append(keyword)
                continue
        
        # Check for lemmatized/synonym matches
        found_match = False
        
        # Check each synonym group
        for base, synonyms in SYNONYM_GROUPS.items():
            if keyword in synonyms:
                for synonym in synonyms:
                    if synonym in normalized_cv:
                        matched.append(keyword)
                        found_match = True
                        break
                if found_match:
                    break
        
        # Check for partial matches (for longer phrases)
        if not found_match and len(keyword_words) > 2:
            # Check if at least 2/3 of the words match
            matches = 0
            for word in keyword_words:
                if word in normalized_cv:
                    matches += 1
            if matches >= len(keyword_words) * 0.67:  # 2/3 threshold
                matched.append(keyword)
                found_match = True
        
        if not found_match:
            missing.append(keyword)
    
    return {
        "matched_keywords": matched,
        "missing_keywords": missing[:7]  # Top 7 missing keywords
    }

def generate_bullet_suggestions(missing_keywords: List[str]) -> List[str]:
    """Generate 4-5 bullet suggestions weaving missing keywords naturally"""
    templates = [
        "Conducted {keyword} to inform design decisions and improve user experience.",
        "Developed {keyword} strategies that enhanced product usability and accessibility.",
        "Implemented {keyword} processes that streamlined user workflows and increased efficiency.",
        "Created {keyword} frameworks that improved stakeholder alignment and project outcomes.",
        "Led {keyword} initiatives that resulted in measurable improvements in user satisfaction.",
        "Established {keyword} methodologies that enhanced team collaboration and project delivery.",
        "Applied {keyword} techniques to optimize user interface design and interaction patterns.",
        "Built {keyword} systems that improved data visualization and analytical capabilities."
    ]
    
    suggestions = []
    used_keywords = set()
    
    for keyword in missing_keywords[:5]:
        if keyword in used_keywords:
            continue
        
        template = random.choice(templates)
        suggestion = template.format(keyword=keyword)
        
        # Ensure suggestion is <= 20 words
        words = suggestion.split()
        if len(words) <= 20:
            suggestions.append(suggestion)
            used_keywords.add(keyword)
    
    # Fill remaining slots if needed
    while len(suggestions) < 4:
        generic_suggestions = [
            "Collaborated with cross-functional teams to deliver user-centered solutions.",
            "Applied design thinking methodologies to solve complex user experience challenges.",
            "Implemented accessibility best practices to ensure inclusive design standards.",
            "Conducted user research to validate design decisions and improve usability."
        ]
        
        suggestion = random.choice(generic_suggestions)
        if suggestion not in suggestions:
            suggestions.append(suggestion)
    
    return suggestions[:5]

def get_debug_info(jd_text: str) -> Dict[str, List[str]]:
    """Get debug information about dropped and kept examples"""
    normalized_text = normalize_text(jd_text)
    words = normalized_text.split()
    
    dropped_examples = []
    kept_examples = []
    
    # Check single words
    for word in words:
        if len(word) >= 3:
            if is_generic_word(word) and not is_whitelisted_single(word):
                dropped_examples.append(word)
            else:
                kept_examples.append(word)
    
    # Check phrases
    phrases = extract_phrases(normalized_text)
    for phrase in phrases:
        phrase_words = phrase.split()
        if any(is_generic_word(word) for word in phrase_words) and not is_preferred_pattern(phrase):
            dropped_examples.append(phrase)
        else:
            kept_examples.append(phrase)
    
    return {
        "dropped_examples": list(set(dropped_examples))[:10],
        "kept_examples": list(set(kept_examples))[:10]
    }

def extract_resume_keywords(resume_text: str) -> List[str]:
    """Extract keywords from resume text using the same logic as job description"""
    return extract_ats_keywords(resume_text)

def extract_job_keywords_focused(job_description: str) -> List[str]:
    """Extract keywords from job description using the same logic as ATS extractor"""
    return extract_ats_keywords(job_description)

def calculate_similarity(resume_keywords: Set[str], job_keywords: Set[str]) -> float:
    """Calculate similarity between resume and job description keywords"""
    if not job_keywords:
        return 0.0
    
    intersection = resume_keywords.intersection(job_keywords)
    union = resume_keywords.union(job_keywords)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union) * 100

@app.post("/extract-keywords")
async def extract_keywords(
    jd_text: str = Form(...),
    cv_text: str = Form(...)
) -> Dict[str, Any]:
    """Extract ATS keywords and match against CV"""
    try:
        # Limit input size to prevent timeout
        if len(jd_text) > 10000 or len(cv_text) > 10000:
            raise HTTPException(status_code=400, detail="Input text too long. Please limit to 10,000 characters each.")
        
        # Extract keywords from both JD and CV
        jd_keywords = extract_ats_keywords(jd_text)
        cv_keywords = extract_ats_keywords(cv_text)
        
        # Match keywords against CV
        matching_result = match_keywords_to_cv(jd_keywords, cv_text)
        
        # Generate bullet suggestions
        bullet_suggestions = generate_bullet_suggestions(matching_result["missing_keywords"])
        
        # Get debug information
        debug_info = get_debug_info(jd_text)
        
        # Return result in specified format
        result = {
            "all_keywords": jd_keywords,
            "resume_keywords": cv_keywords,
            "matched_keywords": matching_result["matched_keywords"],
            "missing_keywords": matching_result["missing_keywords"],
            "bullet_suggestions": bullet_suggestions,
            "debug": debug_info
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "ATS Resume Checker API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is working!"}

@app.get("/test")
async def test_interface():
    """Serve the test interface HTML"""
    try:
        with open("test_interface.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": "Test interface not found"}

@app.get("/simple")
async def simple_test():
    """Serve the simple test interface HTML"""
    try:
        with open("simple_test.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": "Simple test interface not found"}

@app.post("/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        # Basic validation
        if not job_description or len(job_description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Job description must be at least 10 characters")
        
        if not resume_file:
            raise HTTPException(status_code=400, detail="Resume file is required")
        
        # Read resume content
        resume_content = await resume_file.read()
        resume_text = resume_content.decode('utf-8', errors='ignore')
        
        # Extract keywords from both resume and job description using ATS extractor
        resume_keywords = extract_ats_keywords(resume_text)
        job_keywords = extract_ats_keywords(job_description)
        
        # Convert to sets for comparison
        resume_keywords_set = set(resume_keywords)
        job_keywords_set = set(job_keywords)
        
        # Find matching and missing keywords
        matching_keywords = list(resume_keywords_set.intersection(job_keywords_set))
        missing_keywords = list(job_keywords_set - resume_keywords_set)
        
        # Generate bullet suggestions for missing keywords
        bullet_suggestions = generate_bullet_suggestions(missing_keywords[:7])
        
        # Calculate scores
        text_similarity = calculate_similarity(resume_keywords_set, job_keywords_set)
        keyword_coverage = len(matching_keywords) / len(job_keywords_set) * 100 if job_keywords_set else 0
        overall_score = (text_similarity + keyword_coverage) / 2
        
        # Simple file info
        file_info = {
            "filename": resume_file.filename,
            "size": resume_file.size,
            "content_type": resume_file.content_type
        }
        
        # Analysis result with new structure
        result = {
            "score": round(overall_score, 1),
            "textSimilarity": round(text_similarity, 1),
            "keywordCoverage": round(keyword_coverage, 1),
            "all_keywords": job_keywords[:30],  # Top 30 keywords from job description
            "resume_keywords": resume_keywords[:30],  # Top 30 keywords from resume
            "matched_keywords": matching_keywords[:15],  # Keywords present in both
            "missing_keywords": missing_keywords[:7],  # Top 7 missing keywords
            "bullet_suggestions": bullet_suggestions,  # 4-5 bullet suggestions
            "file_info": file_info,
            "job_description": job_description[:100] + "..." if len(job_description) > 100 else job_description,
            "message": "Analysis completed successfully!"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
