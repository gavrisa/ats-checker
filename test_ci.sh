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
