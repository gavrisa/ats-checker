@echo off
REM ATS Checker - Private Test Environment Startup Script for Windows
REM This script starts both the backend API and frontend for local testing

echo 🚀 Starting ATS Checker Private Test Environment...
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: npm is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Dependencies checked successfully

REM Start Backend API
echo.
echo 🔧 Starting Backend API...
cd api

REM Check if port 8000 is already in use (Windows)
netstat -an | findstr :8000 >nul
if not errorlevel 1 (
    echo ⚠️  Port 8000 is already in use. Please stop the existing process manually.
    echo    You can use: netstat -ano | findstr :8000
    echo    Then: taskkill /PID <PID> /F
    pause
)

REM Start backend in background
echo    Starting Python backend on port 8000...
start /B python main.py > backend.log 2>&1

REM Wait for backend to start
echo    Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Backend API started successfully on http://localhost:8000
) else (
    echo ❌ Failed to start backend API
    pause
    exit /b 1
)

cd ..

REM Start Frontend
echo.
echo 🎨 Starting Frontend...
cd web

REM Check if port 3000 is already in use (Windows)
netstat -an | findstr :3000 >nul
if not errorlevel 1 (
    echo ⚠️  Port 3000 is already in use. Please stop the existing process manually.
    echo    You can use: netstat -ano | findstr :3000
    echo    Then: taskkill /PID <PID> /F
    pause
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo    Installing frontend dependencies...
    npm install
)

REM Start frontend in background
echo    Starting Next.js frontend on port 3000...
start /B npm run dev > frontend.log 2>&1

REM Wait for frontend to start
echo    Waiting for frontend to start...
timeout /t 10 /nobreak >nul

REM Check if frontend is running
curl -s http://localhost:3000 >nul 2>&1
if not errorlevel 1 (
    echo ✅ Frontend started successfully on http://localhost:3000
) else (
    echo ❌ Failed to start frontend
    pause
    exit /b 1
)

cd ..

echo.
echo 🎉 Test Environment Started Successfully!
echo ==========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo.
echo 📋 Available Endpoints:
echo    • Health Check: http://localhost:8000/health
echo    • Test Interface: http://localhost:8000/test
echo    • Simple Test: http://localhost:8000/simple
echo    • File Upload Test: http://localhost:8000/upload
echo.
echo 📁 Log Files:
echo    • Backend: api\backend.log
echo    • Frontend: web\frontend.log
echo.
echo 🔄 To stop the test environment, close this window and stop the processes manually
echo    You can use Task Manager or: taskkill /IM python.exe /F && taskkill /IM node.exe /F
echo.

REM Keep window open
pause








