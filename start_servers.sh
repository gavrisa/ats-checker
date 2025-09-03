#!/bin/bash

echo "🚀 Starting ATS Checker Servers..."

# Function to kill existing processes
kill_existing() {
    echo "🔄 Stopping existing servers..."
    pkill -f "python3 main.py" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    sleep 2
}

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend Server (Port 8000)..."
    cd api
    python3 main.py &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend Server (Port 3000)..."
    cd web
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started with PID: $FRONTEND_PID"
    cd ..
}

# Function to check if servers are running
check_servers() {
    echo "🔍 Checking server status..."
    sleep 5
    
    if lsof -i :8000 >/dev/null 2>&1; then
        echo "✅ Backend is running on port 8000"
    else
        echo "❌ Backend is not running"
        return 1
    fi
    
    if lsof -i :3000 >/dev/null 2>&1; then
        echo "✅ Frontend is running on port 3000"
    else
        echo "❌ Frontend is not running"
        return 1
    fi
    
    return 0
}

# Function to show URLs
show_urls() {
    echo ""
    echo "🌐 Your ATS Checker is now running!"
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo ""
    echo "💡 Keep this terminal open to keep the servers running"
    echo "🔄 To restart servers, just run this script again"
    echo ""
}

# Main execution
kill_existing
start_backend
start_frontend

# Wait a bit and check if both servers started successfully
if check_servers; then
    show_urls
    
    # Keep the script running and show server logs
    echo "📊 Server logs (Ctrl+C to stop all servers):"
    echo "=========================================="
    
    # Wait for user to stop
    wait
else
    echo "❌ Failed to start servers properly"
    echo "🔧 Please check the error messages above"
    exit 1
fi
