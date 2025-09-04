#!/bin/bash

# Start Frontend with Local Backend Configuration
echo "🚀 Starting Frontend with Local Backend Configuration..."

# Set environment variable for local development
export NEXT_PUBLIC_API_URL=http://localhost:8000

echo "Backend URL: $NEXT_PUBLIC_API_URL"
echo "Starting frontend development server..."

cd web
npm run dev


