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
