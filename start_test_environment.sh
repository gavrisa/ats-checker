#!/bin/bash

# ATS Checker - Private Test Environment Startup Script
# This script starts both the backend API and frontend for local testing

echo "🚀 Starting ATS Checker Private Test Environment..."
echo "=================================================="

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down test environment..."
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "✅ Test environment stopped."
    exit 0
}

# Set up signal handlers for cleanup
trap cleanup SIGINT SIGTERM

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed or not in PATH"
    exit 1
fi

echo "✅ Dependencies checked successfully"

# Navigate to the project directory
cd "$(dirname "$0")"

# Start Backend API
echo ""
echo "🔧 Starting Backend API..."
cd api

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Stopping existing process..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

# Start backend in background
echo "   Starting Python backend on port 8000..."
python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "   Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API started successfully on http://localhost:8000"
else
    echo "❌ Failed to start backend API"
    exit 1
fi

cd ..

# Start Frontend
echo ""
echo "🎨 Starting Frontend..."
cd web

# Check if port 3000 is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is already in use. Stopping existing process..."
    lsof -ti:3000 | xargs kill -9
    sleep 2
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "   Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
echo "   Starting Next.js frontend on port 3000..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "   Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend started successfully on http://localhost:3000"
else
    echo "❌ Failed to start frontend"
    exit 1
fi

cd ..

echo ""
echo "🎉 Test Environment Started Successfully!"
echo "=========================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo ""
echo "📋 Available Endpoints:"
echo "   • Health Check: http://localhost:8000/health"
echo "   • Test Interface: http://localhost:8000/test"
echo "   • Simple Test: http://localhost:8000/simple"
echo "   • File Upload Test: http://localhost:8000/upload"
echo ""
echo "📁 Log Files:"
echo "   • Backend: api/backend.log"
echo "   • Frontend: web/frontend.log"
echo ""
echo "🔄 To stop the test environment, press Ctrl+C"
echo ""

# Keep script running and monitor processes
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process stopped unexpectedly"
        break
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process stopped unexpectedly"
        break
    fi
    
    sleep 5
done

cleanup

