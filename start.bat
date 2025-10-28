@echo off
REM CodeSense AI Startup Script for Windows

echo 🚀 Starting CodeSense AI...

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy env.example .env
    echo 📝 Please edit .env file with your API keys before running again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check if frontend dependencies are installed
if not exist frontend\node_modules (
    echo 📥 Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

REM Start the application
echo 🎯 Starting CodeSense AI...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the application

REM Start backend
start "CodeSense AI Backend" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Start frontend
cd frontend
start "CodeSense AI Frontend" cmd /k "npm start"
cd ..

echo 👋 CodeSense AI started! Check the opened windows for logs.
pause
