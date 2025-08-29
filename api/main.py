from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="ATS Resume Checker", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ATS Resume Checker API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is working!"}

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
        
        # Simple file info
        file_info = {
            "filename": resume_file.filename,
            "size": resume_file.size,
            "content_type": resume_file.content_type
        }
        
        # Mock analysis result
        result = {
            "ats_score": 75,
            "keywords_found": ["design", "user", "interface"],
            "keywords_missing": ["prototyping", "research"],
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
