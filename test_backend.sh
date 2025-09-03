#!/bin/bash

# Backend Test Script
echo "🧪 Testing Backend API..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}❌ Backend not running. Please start it with: cd api && uvicorn main:app --reload${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running${NC}"

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:8000/health | jq '.' || echo "Health check response received"

# Test keyword extraction
echo -e "\n${YELLOW}Testing keyword extraction...${NC}"
curl -X POST http://localhost:8000/analyze \
  -F "resume_file=@test_data/sample_resume.txt" \
  -F "job_description=$(cat test_data/sample_job_description.txt)" \
  --max-time 30 | jq '.' > test_results/backend_test_result.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend test completed successfully${NC}"
    echo "Results saved to test_results/backend_test_result.json"
    
    # Show key metrics
    echo -e "\n${YELLOW}Key Metrics:${NC}"
    jq -r '"ATS Score: " + (.score | tostring) + "/100"' test_results/backend_test_result.json
    jq -r '"Text Similarity: " + (.textSimilarity | tostring) + "%"' test_results/backend_test_result.json
    jq -r '"Keyword Coverage: " + (.keywordCoverage | tostring) + "%"' test_results/backend_test_result.json
    jq -r '"Total Keywords: " + (.all_keywords | length | tostring)' test_results/backend_test_result.json
    jq -r '"Matched Keywords: " + (.matched_keywords | length | tostring)' test_results/backend_test_result.json
    jq -r '"Missing Keywords: " + (.missing_keywords | length | tostring)' test_results/backend_test_result.json
else
    echo -e "${RED}❌ Backend test failed${NC}"
    exit 1
fi
