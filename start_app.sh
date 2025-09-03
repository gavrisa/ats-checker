#!/bin/bash

echo "🚀 Starting ATS Checker Application..."

# Kill any existing processes
echo "🔄 Stopping existing servers..."
pkill -f "python3 main.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 2

# Start backend
echo "🔧 Starting Backend (Port 8000)..."
cd api
python3 main.py &
BACKEND_PID=$!
echo "✅ Backend started with PID: $BACKEND_PID"
cd ..

# Start frontend
echo "🎨 Starting Frontend (Port 3000)..."
cd web
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"
cd ..

# Wait and check
echo "⏳ Waiting for servers to start..."
sleep 10

echo ""
echo "🌐 Your ATS Checker is now running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "💡 Keep this terminal open to keep the servers running"
echo "🔄 Press Ctrl+C to stop all servers"
echo ""

# Keep script running
wait
