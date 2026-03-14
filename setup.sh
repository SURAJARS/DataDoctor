#!/bin/bash

echo "🏥 Data Doctor - Setup Guide"
echo "============================"
echo

# Check Python
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is required. Please install Python 3.9+"
    exit 1
fi

# Check Node
echo "✓ Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js is required. Please install Node.js 18+"
    exit 1
fi

# Setup backend
echo
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

echo "✓ Backend setup complete"

# Setup frontend
echo
echo "📦 Setting up frontend..."
cd ../frontend

npm install

echo "✓ Frontend setup complete"

echo
echo "🚀 Setup complete!"
echo
echo "To start the application:"
echo "1. Terminal 1 - Backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   uvicorn main:app --reload"
echo
echo "2. Terminal 2 - Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo
echo "Then visit: http://localhost:3000"
