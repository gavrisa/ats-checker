from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path

# Add parent directory to path to import utils - more robust for deployment
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from utils import (
        extract_text_from_file,
        clean_text,
        extract_keywords_with_scores,
        suggest_missing_keywords,
        compute_similarity,
        select_most_relevant_keywords,
        smart_bullets_for_missing
    )
except ImportError:
    # Fallback for deployment environments
    sys.path.insert(0, str(current_dir))
    from utils import (
        extract_text_from_file,
        clean_text,
        extract_keywords_with_scores,
        suggest_missing_keywords,
        compute_similarity,
        select_most_relevant_keywords,
        smart_bullets_for_missing
    )

app = FastAPI(
    title="ATS Resume Checker API",
    description="Simple and reliable API for analyzing resume compatibility",
    version="2.0.0"
)

# CORS middleware - configured for production and development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:8080",  # Local test interface
        "https://*.vercel.app",   # Vercel frontend
        "https://*.onrender.com", # Render backend
        "*"  # Allow all for now (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ATS Resume Checker API v2.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ats-checker-api-v2"}

@app.post("/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyze resume compatibility with job description.
    """
    try:
        print(f"=== NEW REQUEST ===")
        print(f"File: {resume_file.filename}")
        print(f"Type: {resume_file.content_type}")
        print(f"Size: {resume_file.size if hasattr(resume_file, 'size') else 'unknown'}")
        
        # Validate job description
        if not job_description or len(job_description.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Job description must be at least 50 characters long"
            )
        
        # Extract text from resume
        print("Extracting text from resume...")
        resume_text = await extract_text_from_file(resume_file)
        
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract any text from the resume file"
            )
        
        print(f"Extracted text length: {len(resume_text)}")
        print(f"Text preview: {resume_text[:200]}...")
        
        # Clean and process texts
        resume_text_clean = clean_text(resume_text)
        jd_text_clean = clean_text(job_description)
        
        print(f"Cleaned resume text length: {len(resume_text_clean)}")
        print(f"Cleaned JD text length: {len(jd_text_clean)}")
        
        # Extract keywords and compute scores
        jd_keywords = extract_keywords_with_scores(jd_text_clean, top_n=30)
        jd_keywords_list = [word for word, _ in jd_keywords]
        
        print(f"JD keywords found: {jd_keywords_list[:10]}...")
        
        # Compute similarity and coverage
        text_similarity = compute_similarity(jd_text_clean, resume_text_clean)
        present, missing, _ = suggest_missing_keywords(jd_text_clean, resume_text_clean)
        
        print(f"Text similarity: {text_similarity}")
        print(f"Present keywords: {present}")
        print(f"Missing keywords: {missing}")
        
        # Calculate keyword coverage percentage
        total_keywords = len(present) + len(missing)
        keyword_coverage = (len(present) / total_keywords * 100) if total_keywords > 0 else 0
        
        # Calculate overall score (70% keyword coverage + 30% text similarity)
        overall_score = round(0.7 * keyword_coverage + 0.3 * (text_similarity * 100))
        overall_score = max(0, min(100, overall_score))
        
        # Generate smart bullet suggestions for missing keywords
        relevant_missing = select_most_relevant_keywords(
            [(word, 0) for word in missing], jd_text_clean, top_k=8
        )
        bullet_suggestions = smart_bullets_for_missing(relevant_missing[:5])
        
        # Prepare response
        response = {
            "score": overall_score,
            "textSimilarity": round(text_similarity * 100, 1),
            "keywordCoverage": round(keyword_coverage, 1),
            "jdKeywordsTop30": jd_keywords_list,
            "present": list(present),
            "missing": list(missing),
            "bullets": bullet_suggestions,
            "analysis": {
                "resumeWords": len(resume_text_clean.split()),
                "jdWords": len(jd_text_clean.split()),
                "keywordsFound": len(present),
                "keywordsMissing": len(missing),
                "totalKeywords": total_keywords
            }
        }
        
        print(f"=== REQUEST COMPLETED SUCCESSFULLY ===")
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting ATS Resume Checker API v2.0...")
    print(f"📍 Backend will be available at: http://0.0.0.0:{port}")
    print("🔍 Health check: /health")
    print("📊 Analysis endpoint: /analyze")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
