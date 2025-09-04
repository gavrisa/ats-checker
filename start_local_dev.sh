#!/bin/bash

# Start Local Development Environment
# This script starts both backend and frontend for local development

echo "🚀 Starting ATS Checker Local Development Environment"
echo "=================================================="

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is already running on http://localhost:8000"
else
    echo "🔧 Starting backend on http://localhost:8000..."
    cd api
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started with PID: $BACKEND_PID"
fi

# Wait a moment for backend to start
sleep 3

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null 2>&1 || curl -s http://localhost:3001 > /dev/null 2>&1 || curl -s http://localhost:3002 > /dev/null 2>&1 || curl -s http://localhost:3003 > /dev/null 2>&1; then
    echo "✅ Frontend is already running"
    echo "🌐 Frontend URLs:"
    echo "   - http://localhost:3000"
    echo "   - http://localhost:3001" 
    echo "   - http://localhost:3002"
    echo "   - http://localhost:3003"
else
    echo "🔧 Starting frontend..."
    cd web
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "✅ Frontend started with PID: $FRONTEND_PID"
fi

echo ""
echo "🎉 Local Development Environment Ready!"
echo "=================================================="
echo "📡 Backend:  http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000 (or 3001, 3002, 3003)"
echo ""
echo "🔗 Frontend is now connected to local backend!"
echo "📝 Test the connection by uploading a resume and job description"
echo ""
echo "🛑 To stop: Press Ctrl+C or run 'pkill -f uvicorn' and 'pkill -f next'"
echo ""

# Keep script running
wait


