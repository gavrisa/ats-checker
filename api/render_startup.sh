#!/usr/bin/env bash
# Render startup script for ATS Resume Checker API

echo "🚀 Starting ATS Resume Checker API on Render..."
echo "📍 Environment: $RENDER_ENVIRONMENT"
echo "🔧 Python version: $(python --version)"
echo "📦 Installing dependencies..."

pip install -r requirements.txt

echo "🌐 Starting FastAPI server..."
echo "📍 Backend will be available at: $RENDER_EXTERNAL_URL"
echo "🔍 Health check: $RENDER_EXTERNAL_URL/health"
echo "📊 Analysis endpoint: $RENDER_EXTERNAL_URL/analyze"
echo "=" * 50

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port $PORT
