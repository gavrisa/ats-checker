#!/usr/bin/env python3
"""
Production startup script for Render deployment
"""

import os
import uvicorn
from main import app

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting ATS Resume Checker API v2.0 on Render...")
    print(f"📍 Backend will be available at: http://0.0.0.0:{port}")
    print("🔍 Health check: /health")
    print("📊 Analysis endpoint: /analyze")
    print("=" * 50)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
