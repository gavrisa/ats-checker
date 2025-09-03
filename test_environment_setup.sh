#!/bin/bash

# ATS Checker Test Environment Setup
# This script sets up a complete test environment for both backend and frontend

echo "🚀 Setting up ATS Checker Test Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_info "Setting up test environment..."

# Create test directories
mkdir -p test_data
mkdir -p test_results
mkdir -p test_logs

print_status "Created test directories"

# Create sample test data
cat > test_data/sample_resume.txt << 'EOF'
John Doe
Senior Software Engineer
john.doe@email.com | (555) 123-4567 | LinkedIn: john-doe

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development, 
specializing in Python, React, and cloud technologies. Proven track record of delivering 
scalable applications and leading cross-functional teams.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, Java, SQL
• Frontend: React, Vue.js, HTML5, CSS3, Tailwind CSS
• Backend: Django, Flask, Node.js, Express.js
• Databases: PostgreSQL, MongoDB, Redis
• Cloud Platforms: AWS, Google Cloud Platform, Azure
• DevOps: Docker, Kubernetes, Jenkins, Git, CI/CD
• Machine Learning: TensorFlow, PyTorch, scikit-learn
• Tools: Jira, Confluence, Slack, Figma

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2022 - Present
• Led development of microservices architecture using Python and React
• Implemented CI/CD pipelines reducing deployment time by 40%
• Collaborated with product managers and designers to deliver user-centric solutions
• Mentored junior developers and conducted code reviews
• Optimized database queries improving application performance by 30%

Software Engineer | StartupXYZ | 2020 - 2022
• Developed RESTful APIs using Django and PostgreSQL
• Built responsive web applications with React and TypeScript
• Integrated third-party services and payment processing systems
• Participated in agile development processes and sprint planning
• Implemented automated testing increasing code coverage to 85%

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2016 - 2020

CERTIFICATIONS
• AWS Certified Solutions Architect
• Google Cloud Professional Developer
• Certified Scrum Master (CSM)
EOF

cat > test_data/sample_job_description.txt << 'EOF'
Senior Software Engineer - Full Stack Development

We are seeking a talented Senior Software Engineer to join our dynamic team. 
You will be responsible for developing and maintaining scalable web applications 
using modern technologies.

RESPONSIBILITIES:
• Design and develop full-stack web applications using Python, React, and Node.js
• Build and maintain RESTful APIs and microservices architecture
• Collaborate with cross-functional teams including product managers, designers, and QA
• Implement CI/CD pipelines and DevOps best practices
• Optimize application performance and ensure scalability
• Mentor junior developers and conduct code reviews
• Participate in agile development processes and sprint planning

REQUIREMENTS:
• 5+ years of experience in software development
• Strong proficiency in Python, JavaScript, and TypeScript
• Experience with React, Django, or similar frameworks
• Knowledge of cloud platforms (AWS, GCP, or Azure)
• Experience with databases (PostgreSQL, MongoDB, Redis)
• Familiarity with Docker, Kubernetes, and CI/CD tools
• Strong problem-solving and communication skills
• Experience with agile development methodologies

PREFERRED QUALIFICATIONS:
• Experience with machine learning frameworks (TensorFlow, PyTorch)
• Knowledge of microservices architecture
• Experience with DevOps tools (Jenkins, GitLab CI)
• AWS or Google Cloud certifications
• Experience with testing frameworks and automated testing
• Knowledge of GraphQL and modern API design patterns

BENEFITS:
• Competitive salary and equity package
• Comprehensive health, dental, and vision insurance
• Flexible work arrangements and remote work options
• Professional development opportunities
• Modern office space with latest technology
• Team building events and company retreats
EOF

print_status "Created sample test data"

# Create backend test script
cat > test_backend.sh << 'EOF'
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
EOF

chmod +x test_backend.sh

# Create frontend test script
cat > test_frontend.sh << 'EOF'
#!/bin/bash

# Frontend Test Script
echo "🧪 Testing Frontend..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${RED}❌ Frontend not running. Please start it with: cd web && npm run dev${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend is running${NC}"

# Test frontend accessibility
echo "Testing frontend accessibility..."
curl -s http://localhost:3000 | grep -q "ATS" && echo -e "${GREEN}✅ Frontend accessible${NC}" || echo -e "${RED}❌ Frontend not accessible${NC}"

# Test API connection from frontend
echo "Testing API connection from frontend..."
curl -s http://localhost:3000/api/health 2>/dev/null && echo -e "${GREEN}✅ API connection working${NC}" || echo -e "${YELLOW}⚠️  API connection test skipped (may not be configured)${NC}"

echo -e "${GREEN}✅ Frontend test completed${NC}"
EOF

chmod +x test_frontend.sh

# Create comprehensive test script
cat > run_all_tests.sh << 'EOF'
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
EOF

chmod +x run_all_tests.sh

# Create quick start script
cat > quick_start_test.sh << 'EOF'
#!/bin/bash

# Quick Start Test Environment
echo "🚀 Quick Start Test Environment"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting Backend...${NC}"
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo -e "${YELLOW}Starting Frontend...${NC}"
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Services starting...${NC}"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Services stopped${NC}"
}

trap cleanup EXIT
wait
EOF

chmod +x quick_start_test.sh

# Create test environment documentation
cat > TEST_ENVIRONMENT_README.md << 'EOF'
# ATS Checker Test Environment

This test environment allows you to test both the backend and frontend locally before deploying changes.

## Quick Start

### Option 1: Automated Test Suite
```bash
./run_all_tests.sh
```
This will:
- Start backend and frontend if not running
- Run comprehensive tests
- Generate test reports
- Show results and metrics

### Option 2: Quick Start (Manual Testing)
```bash
./quick_start_test.sh
```
This will:
- Start both services
- Keep them running for manual testing
- Press Ctrl+C to stop

### Option 3: Individual Testing
```bash
# Test backend only
./test_backend.sh

# Test frontend only
./test_frontend.sh
```

## Manual Testing

### Start Backend
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd web
npm run dev
```

### Test URLs
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## Test Data

### Sample Resume
- **File**: `test_data/sample_resume.txt`
- **Content**: Comprehensive software engineer resume with Python, React, AWS experience

### Sample Job Description
- **File**: `test_data/sample_job_description.txt`
- **Content**: Senior Software Engineer position with full-stack requirements

## Test Results

### Backend Test Results
- **File**: `test_results/backend_test_result.json`
- **Contains**: Full API response with scores, keywords, suggestions

### Test Report
- **File**: `test_results/test_report.md`
- **Contains**: Comprehensive test summary and metrics

### Logs
- **Backend Logs**: `test_logs/backend.log`
- **Frontend Logs**: `test_logs/frontend.log`

## Expected Results

### Backend API Response
```json
{
  "score": 8.0,
  "textSimilarity": 27.3,
  "keywordCoverage": 6.7,
  "all_keywords": ["python", "developer", "react", ...],
  "matched_keywords": ["experience", "python", ...],
  "missing_keywords": ["aws", "docker", ...],
  "bullet_suggestions": [...],
  "message": "Analysis completed successfully!"
}
```

### Key Metrics to Check
- **ATS Score**: Should be > 0
- **Text Similarity**: Should be > 0%
- **Keyword Coverage**: Should be > 0%
- **Total Keywords**: Should be ~30
- **Matched Keywords**: Should be > 0
- **Missing Keywords**: Should be > 0

## Troubleshooting

### Backend Not Starting
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Not Starting
```bash
cd web
npm install
npm run dev
```

### API Connection Issues
- Check if backend is running on port 8000
- Check if frontend is running on port 3000
- Verify no firewall blocking ports

### Empty Keywords Issue
- Check backend logs for errors
- Verify smart keyword extractor is working
- Test with sample data

## Development Workflow

1. **Make Changes**: Edit backend or frontend code
2. **Run Tests**: `./run_all_tests.sh`
3. **Check Results**: Review test reports and logs
4. **Fix Issues**: Address any problems found
5. **Re-test**: Run tests again to verify fixes
6. **Deploy**: Push changes to git when ready

## Advanced Testing

### Custom Test Data
Replace `test_data/sample_resume.txt` and `test_data/sample_job_description.txt` with your own test data.

### API Testing
```bash
curl -X POST http://localhost:8000/analyze \
  -F "resume_file=@your_resume.txt" \
  -F "job_description=Your job description here"
```

### Frontend Testing
Open http://localhost:3000 in your browser and test the full user interface.

## Performance Testing

### Load Testing
```bash
# Test multiple requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/analyze \
    -F "resume_file=@test_data/sample_resume.txt" \
    -F "job_description=$(cat test_data/sample_job_description.txt)" &
done
wait
```

### Memory Usage
Monitor memory usage during testing:
```bash
# Monitor backend
ps aux | grep uvicorn

# Monitor frontend
ps aux | grep node
```

## Integration with CI/CD

The test environment can be integrated with CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    ./run_all_tests.sh
    if [ $? -ne 0 ]; then
      echo "Tests failed"
      exit 1
    fi
```

## Support

If you encounter issues:
1. Check the logs in `test_logs/`
2. Review the test report in `test_results/`
3. Verify all services are running
4. Check for port conflicts
5. Ensure all dependencies are installed
EOF

print_status "Created test environment scripts and documentation"

# Create a simple test runner for CI/CD
cat > test_ci.sh << 'EOF'
#!/bin/bash

# CI/CD Test Runner
echo "🧪 Running CI/CD Tests..."

# Start backend
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Test backend
curl -X POST http://localhost:8000/analyze \
  -F "resume_file=@test_data/sample_resume.txt" \
  -F "job_description=$(cat test_data/sample_job_description.txt)" \
  --max-time 30 > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Backend tests passed"
    EXIT_CODE=0
else
    echo "❌ Backend tests failed"
    EXIT_CODE=1
fi

# Cleanup
kill $BACKEND_PID 2>/dev/null

exit $EXIT_CODE
EOF

chmod +x test_ci.sh

print_status "Created CI/CD test runner"

# Install jq if not available (for JSON parsing in tests)
if ! command -v jq &> /dev/null; then
    print_warning "jq not found. Installing for JSON parsing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install jq
        else
            print_warning "Please install jq manually: https://stedolan.github.io/jq/"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y jq
    else
        print_warning "Please install jq manually: https://stedolan.github.io/jq/"
    fi
fi

print_status "Test environment setup complete!"

echo -e "\n${GREEN}🎉 Test Environment Ready!${NC}"
echo -e "${BLUE}📁 Files Created:${NC}"
echo "- test_data/sample_resume.txt"
echo "- test_data/sample_job_description.txt"
echo "- test_backend.sh"
echo "- test_frontend.sh"
echo "- run_all_tests.sh"
echo "- quick_start_test.sh"
echo "- test_ci.sh"
echo "- TEST_ENVIRONMENT_README.md"

echo -e "\n${YELLOW}🚀 Quick Start Commands:${NC}"
echo "1. Run all tests: ./run_all_tests.sh"
echo "2. Quick start: ./quick_start_test.sh"
echo "3. Test backend only: ./test_backend.sh"
echo "4. Test frontend only: ./test_frontend.sh"

echo -e "\n${BLUE}📖 Documentation:${NC}"
echo "- Read TEST_ENVIRONMENT_README.md for detailed instructions"
echo "- Check test_results/ for test outputs"
echo "- Check test_logs/ for service logs"

echo -e "\n${GREEN}✅ Test environment setup complete!${NC}"
