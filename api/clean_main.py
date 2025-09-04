from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import re
from collections import Counter
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Clean ATS Resume Checker", version="2.0.0")

class AnalysisRequest(BaseModel):
    resume_text: str
    jd_text: str

class AnalysisResponse(BaseModel):
    ats_score: float
    text_similarity_pct: float
    keyword_coverage_pct: float
    keywords: Dict[str, List[str]]
    bullets: List[str]

# Comprehensive filler words to remove (no junk like "our/you/but/not")
FILLER_WORDS = {
    # Articles and basic connectors
    'the', 'a', 'an', 'and', 'or', 'but', 'nor', 'yet', 'so',
    
    # Pronouns and possessives
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs',
    'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves',
    
    # Common verbs (basic forms)
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'can', 'could', 'should', 'may', 'might', 'must', 'shall',
    
    # Prepositions
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'down', 'out', 'off', 'over', 'under',
    'between', 'among', 'through', 'during', 'before', 'after', 'since', 'until', 'within', 'without',
    
    # Adverbs and modifiers
    'very', 'really', 'quite', 'rather', 'too', 'so', 'as', 'just', 'only', 'even', 'still', 'also',
    'well', 'much', 'many', 'few', 'little', 'some', 'any', 'all', 'both', 'each', 'every',
    
    # Common job posting words (not job-related)
    'role', 'candidate', 'salary', 'compensation', 'benefits', 'package', 'perks', 'bonus',
    'position', 'job', 'work', 'employment', 'hiring', 'recruiting', 'applicant',
    'team', 'company', 'organization', 'business', 'firm', 'corporation',
    
    # Generic words
    'thing', 'way', 'time', 'day', 'year', 'month', 'week', 'hour', 'minute',
    'place', 'area', 'space', 'room', 'building', 'office', 'location',
    'person', 'people', 'someone', 'anyone', 'everyone', 'nobody',
    
    # Basic adjectives (not job-specific)
    'good', 'bad', 'big', 'small', 'new', 'old', 'young', 'high', 'low', 'long', 'short',
    'easy', 'hard', 'simple', 'complex', 'important', 'necessary', 'required', 'needed',
    
    # Filler words
    'just', 'really', 'very', 'quite', 'rather', 'somewhat', 'kind', 'sort', 'type',
    'like', 'such', 'other', 'another', 'different', 'same', 'similar', 'various',
    'several', 'many', 'few', 'some', 'any', 'all', 'both', 'each', 'every',
    
    # Time and frequency
    'always', 'never', 'sometimes', 'often', 'usually', 'rarely', 'occasionally',
    'today', 'yesterday', 'tomorrow', 'now', 'then', 'when', 'while', 'during',
    
    # Negation and uncertainty
    'not', 'no', 'never', 'neither', 'none', 'nobody', 'nothing', 'nowhere',
    'maybe', 'perhaps', 'possibly', 'probably', 'definitely', 'certainly',
    
    # Common but not job-specific
    'here', 'there', 'where', 'why', 'how', 'what', 'which', 'who', 'whom',
    'this', 'that', 'these', 'those', 'it', 'its', 'itself'
}

# Fragments to remove
FRAGMENTS = {'re', 've', 'll', 'd', 't', 's', 'm', 'nt'}

# Known keyword mappings for smart bullets
KEYWORD_MAPPINGS = {
    'figma': 'Created high-fidelity prototypes in Figma that improved stakeholder alignment and reduced design iterations by 40%.',
    'user research': 'Planned and conducted user research sessions with 50+ participants, leading to data-driven design decisions.',
    'accessibility': 'Improved accessibility to WCAG standards, ensuring inclusive design for users with diverse abilities.',
    'design system': 'Contributed to building a scalable design system that increased design consistency and developer efficiency.',
    'prototyping': 'Developed interactive prototypes that accelerated user testing and stakeholder feedback cycles.',
    'wireframes': 'Created comprehensive wireframes that streamlined the design-to-development handoff process.',
    'usability testing': 'Conducted usability testing sessions that identified critical UX issues and informed design improvements.',
    'user experience': 'Enhanced user experience through iterative design improvements based on user feedback and analytics.',
    'information architecture': 'Restructured information architecture that improved user navigation and task completion rates.',
    'interaction design': 'Designed intuitive interaction patterns that reduced user learning curves and improved engagement.'
}

def extract_text_tokens(text: str) -> List[str]:
    """Tokenize text: lowercase, remove punctuation, split words"""
    if not text:
        return []
    
    # Convert to lowercase and remove punctuation
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Split into words and filter out empty strings
    tokens = [word.strip() for word in clean_text.split() if word.strip()]
    return tokens

def extract_keywords(jd_text: str, top_n: int = 30) -> List[str]:
    """Extract exactly 30 job-related keywords, removing all junk words"""
    if not jd_text:
        return []
    
    # Tokenize the text
    tokens = extract_text_tokens(jd_text)
    
    # Remove filler words and fragments
    filtered_tokens = []
    for token in tokens:
        # Skip if it's a filler word
        if token in FILLER_WORDS:
            continue
        # Skip if it's a fragment
        if token in FRAGMENTS:
            continue
        # Skip if it's too short (less than 3 chars)
        if len(token) < 3:
            continue
        # Skip if it's a number
        if token.isdigit():
            continue
        
        filtered_tokens.append(token)
    
    # Count frequencies
    word_counts = Counter(filtered_tokens)
    
    # Get top keywords by frequency, ensuring we get enough to fill 30 slots
    all_candidates = [word for word, count in word_counts.most_common(top_n * 2)]
    
    # Dynamically remove company names (detect capitalized names in original text)
    company_names = set()
    lines = jd_text.split('\n')
    for line in lines:
        words = line.split()
        for word in words:
            # Check if word starts with capital and is longer than 3 chars
            if word[0].isupper() and len(word) > 3 and word.isalpha():
                company_names.add(word.lower())
    
    # Remove company names and ensure exactly 30 keywords
    final_keywords = []
    for kw in all_candidates:
        if kw not in company_names and len(final_keywords) < top_n:
            final_keywords.append(kw)
    
    # Always ensure we have exactly 30 keywords by padding with relevant domain keywords
    if len(final_keywords) < top_n:
        additional_keywords = [
            'design', 'user', 'experience', 'interface', 'research', 'testing', 'prototyping', 'wireframing',
            'accessibility', 'usability', 'interaction', 'visual', 'graphic', 'creative', 'innovation', 'strategy',
            'collaboration', 'communication', 'leadership', 'management', 'planning', 'analysis', 'development',
            'implementation', 'evaluation', 'optimization', 'improvement', 'quality', 'efficiency', 'effectiveness',
            'methodology', 'framework', 'process', 'workflow', 'solution', 'approach', 'technique', 'method',
            'tool', 'platform', 'software', 'application', 'system', 'architecture', 'structure', 'organization'
        ]
        
        for kw in additional_keywords:
            if kw not in final_keywords and len(final_keywords) < top_n:
                final_keywords.append(kw)
    
    # Ensure we return exactly 30 keywords
    logger.info(f"extract_keywords returning {len(final_keywords)} keywords")
    return final_keywords[:top_n]

def compare_keywords(jd_keywords: List[str], resume_text: str) -> Dict[str, List[str]]:
    """Compare JD keywords against resume text"""
    if not jd_keywords or not resume_text:
        return {"present": [], "missing": jd_keywords}
    
    resume_tokens = set(extract_text_tokens(resume_text))
    
    present = []
    missing = []
    
    for keyword in jd_keywords:
        if keyword in resume_tokens:
            present.append(keyword)
        else:
            missing.append(keyword)
    
    return {"present": present, "missing": missing}

def keyword_coverage(present: List[str], jd_keywords: List[str]) -> float:
    """Calculate keyword coverage percentage"""
    if not jd_keywords:
        return 0.0
    
    coverage = len(present) / len(jd_keywords) * 100
    return round(coverage, 1)

def text_similarity(resume_text: str, jd_text: str) -> float:
    """Calculate Jaccard similarity between resume and JD"""
    if not resume_text or not jd_text:
        return 0.0
    
    resume_tokens = set(extract_text_tokens(resume_text))
    jd_tokens = set(extract_text_tokens(jd_text))
    
    if not resume_tokens or not jd_tokens:
        return 0.0
    
    intersection = len(resume_tokens.intersection(jd_tokens))
    union = len(resume_tokens.union(jd_tokens))
    
    similarity = (intersection / union) * 100
    return round(similarity, 1)

def ats_score(coverage: float, similarity: float) -> float:
    """Calculate weighted ATS score: 60% coverage + 40% similarity"""
    score = (coverage * 0.6) + (similarity * 0.4)
    return round(score, 1)

def smart_bullets(missing_keywords: List[str]) -> List[str]:
    """Generate bullet suggestions ONLY from top 7 missing keywords"""
    bullets = []
    
    # Only process the top 7 most important missing keywords
    top_missing = missing_keywords[:7]
    
    for keyword in top_missing:
        if keyword in KEYWORD_MAPPINGS:
            # Use known mapping for important keywords
            bullets.append(KEYWORD_MAPPINGS[keyword])
        else:
            # Fallback template for other keywords
            fallback = f"Incorporated '{keyword}' into workflow with measurable impact on project outcomes and team efficiency."
            bullets.append(fallback)
    
    return bullets

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest):
    """Analyze resume against job description"""
    try:
        # Validate input
        if not request.resume_text.strip():
            raise HTTPException(status_code=400, detail="Resume text cannot be empty")
        
        if not request.jd_text.strip():
            raise HTTPException(status_code=400, detail="Job description text cannot be empty")
        
        logger.info(f"Starting analysis - Resume: {len(request.resume_text)} chars, JD: {len(request.jd_text)} chars")
        
        # Extract keywords from job description
        jd_keywords = extract_keywords(request.jd_text, top_n=30)
        logger.info(f"Extracted {len(jd_keywords)} keywords from JD (target: 30)")
        
        # FORCE padding to ensure exactly 30 keywords
        print(f"🔥 FORCING padding to reach 30 keywords")  # Direct print for debugging
        logger.info(f"FORCING padding to reach 30 keywords")
        additional_keywords = [
            'design', 'user', 'experience', 'interface', 'research', 'testing', 'prototyping', 'wireframing',
            'accessibility', 'usability', 'interaction', 'visual', 'graphic', 'creative', 'innovation', 'strategy',
            'collaboration', 'communication', 'leadership', 'management', 'planning', 'analysis', 'development',
            'implementation', 'evaluation', 'optimization', 'improvement', 'quality', 'efficiency', 'effectiveness',
            'methodology', 'framework', 'process', 'workflow', 'solution', 'approach', 'technique', 'method',
            'tool', 'platform', 'software', 'application', 'system', 'architecture', 'structure', 'organization'
        ]
        
        # Add keywords until we reach 30
        for kw in additional_keywords:
            if kw not in jd_keywords and len(jd_keywords) < 30:
                jd_keywords.append(kw)
                logger.info(f"Added keyword: {kw}")
        
        logger.info(f"After FORCED padding: {len(jd_keywords)} keywords")
        
        # Ensure we have exactly 30 keywords
        if len(jd_keywords) < 30:
            logger.warning(f"Still only have {len(jd_keywords)} keywords after FORCED padding!")
        elif len(jd_keywords) > 30:
            jd_keywords = jd_keywords[:30]
            logger.info(f"Truncated to exactly 30 keywords")
        else:
            logger.info(f"Perfect! Exactly 30 keywords")
        
        # Compare keywords against resume
        comparison = compare_keywords(jd_keywords, request.resume_text)
        present_keywords = comparison["present"]
        missing_keywords = comparison["missing"]
        
        # Calculate metrics
        coverage_pct = keyword_coverage(present_keywords, jd_keywords)
        similarity_pct = text_similarity(request.resume_text, request.jd_text)
        final_score = ats_score(coverage_pct, similarity_pct)
        
        # Generate smart bullets
        bullet_suggestions = smart_bullets(missing_keywords)
        
        # Build response with exactly 30 keywords and top 7 missing
        response = AnalysisResponse(
            ats_score=final_score,
            text_similarity_pct=similarity_pct,
            keyword_coverage_pct=coverage_pct,
            keywords={
                "top30": jd_keywords[:30],  # Ensure exactly 30
                "present": present_keywords,
                "missing": missing_keywords[:7]  # Top 7 most important missing
            },
            bullets=bullet_suggestions
        )
        
        logger.info(f"Analysis completed - Score: {final_score}, Coverage: {coverage_pct}%, Similarity: {similarity_pct}%")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Clean ATS Resume Checker is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Clean ATS Resume Checker API", "version": "2.0.0"}

@app.get("/test")
async def test_interface():
    """Serve the test interface HTML"""
    try:
        with open("clean_test.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": "Test interface not found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Clean ATS Resume Checker on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
