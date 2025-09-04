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


