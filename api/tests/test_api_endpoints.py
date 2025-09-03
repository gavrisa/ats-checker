"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import json
import tempfile
import os

class TestRootEndpoints:
    """Test basic API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "ATS Resume Checker API" in data["message"]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data

class TestExtractKeywordsEndpoint:
    """Test the extract-keywords endpoint"""
    
    def test_extract_keywords_success(self, client, sample_jd, sample_cv):
        """Test successful keyword extraction"""
        response = client.post(
            "/extract-keywords",
            data={"jd_text": sample_jd, "cv_text": sample_cv}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["all_keywords", "matched_keywords", "missing_keywords", "bullet_suggestions", "debug"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["all_keywords"], list)
        assert isinstance(data["matched_keywords"], list)
        assert isinstance(data["missing_keywords"], list)
        assert isinstance(data["bullet_suggestions"], list)
        assert isinstance(data["debug"], dict)
        
        # Check reasonable limits
        assert len(data["all_keywords"]) <= 30
        assert len(data["missing_keywords"]) <= 7
        assert len(data["bullet_suggestions"]) <= 5
    
    def test_extract_keywords_empty_jd(self, client, sample_cv):
        """Test with empty job description"""
        response = client.post(
            "/extract-keywords",
            data={"jd_text": "", "cv_text": sample_cv}
        )
        
        assert response.status_code == 422  # FastAPI validation error for empty required field
    
    def test_extract_keywords_empty_cv(self, client, sample_jd):
        """Test with empty CV"""
        response = client.post(
            "/extract-keywords",
            data={"jd_text": sample_jd, "cv_text": ""}
        )
        
        assert response.status_code == 422  # FastAPI validation error for empty required field
    
    def test_extract_keywords_missing_fields(self, client):
        """Test with missing required fields"""
        # Missing CV text
        response = client.post(
            "/extract-keywords",
            data={"jd_text": "sample text"}
        )
        assert response.status_code == 422  # Validation error
        
        # Missing JD text
        response = client.post(
            "/extract-keywords",
            data={"cv_text": "sample text"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_extract_keywords_too_long(self, client):
        """Test with text that's too long"""
        long_text = "word " * 30000  # 30,000 words
        
        response = client.post(
            "/extract-keywords",
            data={"jd_text": long_text, "cv_text": "sample cv"}
        )
        
        assert response.status_code == 400
        assert "too long" in response.json()["detail"].lower()
    
    def test_extract_keywords_whitespace_only(self, client):
        """Test with whitespace-only text"""
        response = client.post(
            "/extract-keywords",
            data={"jd_text": "   \n\t   ", "cv_text": "   \n\t   "}
        )
        
        assert response.status_code == 400

class TestAnalyzeEndpoint:
    """Test the analyze endpoint"""
    
    def test_analyze_success(self, client, sample_jd):
        """Test successful resume analysis"""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sample resume content with user research and accessibility skills")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/analyze",
                    files={"resume_file": ("test_resume.txt", f, "text/plain")},
                    data={"job_description": sample_jd}
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            required_fields = [
                "score", "textSimilarity", "keywordCoverage",
                "all_keywords", "matched_keywords", "missing_keywords",
                "bullet_suggestions", "file_info", "message"
            ]
            for field in required_fields:
                assert field in data
            
            # Check score ranges
            assert 0 <= data["score"] <= 100
            assert 0 <= data["textSimilarity"] <= 100
            assert 0 <= data["keywordCoverage"] <= 100
            
            # Check file info
            assert data["file_info"]["filename"] == "test_resume.txt"
            assert data["file_info"]["content_type"] == "text/plain"
        
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_analyze_missing_file(self, client, sample_jd):
        """Test analyze endpoint without file"""
        response = client.post(
            "/analyze",
            data={"job_description": sample_jd}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_missing_job_description(self, client):
        """Test analyze endpoint without job description"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as f:
            f.write("Sample resume content")
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post(
                    "/analyze",
                    files={"resume_file": ("test_resume.txt", file, "text/plain")}
                )
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_short_job_description(self, client):
        """Test analyze endpoint with too short job description"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as f:
            f.write("Sample resume content")
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post(
                    "/analyze",
                    files={"resume_file": ("test_resume.txt", file, "text/plain")},
                    data={"job_description": "short"}
                )
        
        assert response.status_code == 400

class TestStaticEndpoints:
    """Test static file serving endpoints"""
    
    def test_test_endpoint_file_not_found(self, client):
        """Test /test endpoint when file doesn't exist"""
        response = client.get("/test")
        # Should return error message since test_interface.html doesn't exist
        assert response.status_code == 200
        # The endpoint returns JSON when file is not found
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "error" in data
    
    def test_simple_endpoint_file_not_found(self, client):
        """Test /simple endpoint when file doesn't exist"""
        response = client.get("/simple")
        # Should return error message since simple_test.html doesn't exist
        assert response.status_code == 200
        # The endpoint returns JSON when file is not found
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "error" in data
    
    def test_upload_endpoint_file_not_found(self, client):
        """Test /upload endpoint when file doesn't exist"""
        response = client.get("/upload")
        # Should return error message since simple_file_upload.html doesn't exist
        assert response.status_code == 200
        # The endpoint returns JSON when file is not found
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "error" in data

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_endpoint(self, client):
        """Test request to non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_wrong_method(self, client):
        """Test wrong HTTP method"""
        response = client.get("/extract-keywords")  # Should be POST
        assert response.status_code == 405  # Method not allowed
    
    def test_malformed_json(self, client):
        """Test malformed request data"""
        response = client.post(
            "/extract-keywords",
            data={"jd_text": None, "cv_text": None}  # Invalid data
        )
        assert response.status_code in [400, 422]  # Bad request or validation error
