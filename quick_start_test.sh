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
