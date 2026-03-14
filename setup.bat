@echo off
REM Data Doctor Setup for Windows

echo 🏥 Data Doctor - Setup Guide
echo ============================
echo.

REM Check Python
echo ✓ Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python is required. Please install Python 3.9+
    exit /b 1
)

REM Check Node
echo ✓ Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Node.js is required. Please install Node.js 18+
    exit /b 1
)

REM Setup backend
echo.
echo 📦 Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

echo ✓ Backend setup complete

REM Setup frontend
echo.
echo 📦 Setting up frontend...
cd ..\frontend

call npm install

echo ✓ Frontend setup complete

echo.
echo 🚀 Setup complete!
echo.
echo To start the application:
echo 1. Terminal 1 - Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload
echo.
echo 2. Terminal 2 - Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo Then visit: http://localhost:3000
