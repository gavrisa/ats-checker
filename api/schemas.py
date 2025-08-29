from pydantic import BaseModel, Field
from typing import List, Optional

class AnalysisRequest(BaseModel):
    """Request model for resume analysis"""
    job_description: str = Field(..., min_length=50, description="Job description text")

class AnalysisResponse(BaseModel):
    """Response model for resume analysis"""
    score: int = Field(..., ge=0, le=100, description="Overall ATS match score (0-100)")
    textSimilarity: float = Field(..., ge=0, le=100, description="Text similarity percentage")
    keywordCoverage: float = Field(..., ge=0, le=100, description="Keyword coverage percentage")
    jdKeywordsTop30: List[str] = Field(..., description="Top 30 keywords from job description")
    present: List[str] = Field(..., description="Keywords found in resume")
    missing: List[str] = Field(..., description="Keywords missing from resume")
    bullets: List[str] = Field(..., description="Smart bullet suggestions for missing keywords")
    analysis: dict = Field(..., description="Additional analysis metrics")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error description")
    status_code: int = Field(..., description="HTTP status code")
