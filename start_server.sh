#!/bin/bash

# Kill any existing server processes
echo "🔄 Stopping any existing server..."
pkill -f "python3 main.py" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Start the server
echo "🚀 Starting ATS Keyword Extractor server..."
cd api
python3 main.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Server is running on http://localhost:8000"
    echo "📝 You can now:"
    echo "   - Run: python3 test_ats_extractor.py"
    echo "   - Open: test_ats_interface.html in your browser"
    echo "   - Use the API directly"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    # Keep the script running
    wait $SERVER_PID
else
    echo "❌ Failed to start server"
    exit 1
fi

