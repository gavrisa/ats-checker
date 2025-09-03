#!/bin/bash

# Comprehensive Test Runner
echo "🚀 Running Comprehensive ATS Checker Tests..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create test results directory
mkdir -p test_results
mkdir -p test_logs

# Start services if not running
echo -e "${BLUE}Checking services...${NC}"

# Check backend
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}⚠️  Backend not running. Starting backend...${NC}"
    cd api
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../test_logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    sleep 5
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${GREEN}✅ Backend already running${NC}"
fi

# Check frontend
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${YELLOW}⚠️  Frontend not running. Starting frontend...${NC}"
    cd web
    npm run dev > ../test_logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    sleep 10
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${GREEN}✅ Frontend already running${NC}"
fi

# Run backend tests
echo -e "\n${BLUE}Running Backend Tests...${NC}"
./test_backend.sh

# Run frontend tests
echo -e "\n${BLUE}Running Frontend Tests...${NC}"
./test_frontend.sh

# Generate test report
echo -e "\n${BLUE}Generating Test Report...${NC}"
cat > test_results/test_report.md << 'REPORT'
# ATS Checker Test Report

## Test Environment
- **Date**: $(date)
- **Backend URL**: http://localhost:8000
- **Frontend URL**: http://localhost:3000

## Test Results

### Backend Tests
$(if [ -f test_results/backend_test_result.json ]; then
    echo "✅ Backend tests completed successfully"
    echo "- ATS Score: $(jq -r '.score' test_results/backend_test_result.json)/100"
    echo "- Text Similarity: $(jq -r '.textSimilarity' test_results/backend_test_result.json)%"
    echo "- Keyword Coverage: $(jq -r '.keywordCoverage' test_results/backend_test_result.json)%"
    echo "- Total Keywords: $(jq -r '.all_keywords | length' test_results/backend_test_result.json)"
    echo "- Matched Keywords: $(jq -r '.matched_keywords | length' test_results/backend_test_result.json)"
    echo "- Missing Keywords: $(jq -r '.missing_keywords | length' test_results/backend_test_result.json)"
else
    echo "❌ Backend tests failed"
fi)

### Frontend Tests
$(if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend tests completed successfully"
else
    echo "❌ Frontend tests failed"
fi)

## Sample Data Used
- **Resume**: test_data/sample_resume.txt
- **Job Description**: test_data/sample_job_description.txt

## Logs
- **Backend Logs**: test_logs/backend.log
- **Frontend Logs**: test_logs/frontend.log

## Next Steps
1. Review test results
2. Check logs for any issues
3. Make improvements based on findings
4. Re-run tests after changes
REPORT

echo -e "${GREEN}✅ Test report generated: test_results/test_report.md${NC}"

# Show summary
echo -e "\n${GREEN}🎉 Test Environment Setup Complete!${NC}"
echo -e "${BLUE}📊 Test Results:${NC}"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- Test Report: test_results/test_report.md"
echo "- Backend Results: test_results/backend_test_result.json"
echo "- Logs: test_logs/"

echo -e "\n${YELLOW}💡 To run tests again: ./run_all_tests.sh${NC}"
echo -e "${YELLOW}💡 To test backend only: ./test_backend.sh${NC}"
echo -e "${YELLOW}💡 To test frontend only: ./test_frontend.sh${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
}

# Set trap for cleanup on exit
trap cleanup EXIT

echo -e "\n${BLUE}Press Ctrl+C to stop all services and exit${NC}"
wait
