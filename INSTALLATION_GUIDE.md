# Installation Guide - Data Doctor 🏥

Complete step-by-step installation guide for Data Doctor.

## Prerequisites

### System Requirements

- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for application + dependencies
- **Internet**: Required for initial setup

### Software Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher (comes with Node.js)
- **Git**: Optional (for cloning)

---

## 1️⃣ System Setup

### Install Python

**Windows:**

```bash
# Download from https://www.python.org/downloads/
# Run installer and ensure "Add Python to PATH" is checked
# Verify installation
python --version
```

**macOS:**

```bash
# Using Homebrew
brew install python3

# Verify
python3 --version
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-venv python3-pip

# Fedora
sudo dnf install python3 python3-venv python3-pip

# Verify
python3 --version
```

### Install Node.js

**Windows/macOS/Linux:**

```bash
# Download from https://nodejs.org/
# Install LTS version
# Verify
node --version
npm --version
```

---

## 2️⃣ Backend Installation

### Step 1: Navigate to Backend Directory

```bash
cd DataDoctor/backend
```

### Step 2: Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This installs:

- FastAPI (web framework)
- Pandas (data manipulation)
- NumPy (numerical computing)
- Scikit-learn (ML utilities)
- Dask (large file handling)
- And more...

### Step 4: Start Backend Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Visit:** http://localhost:8000/docs for API documentation

---

## 3️⃣ Frontend Installation

### Step 1: Open New Terminal/Command Prompt

```bash
cd DataDoctor/frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

**This installs:**

- React
- TypeScript
- Tailwind CSS
- Recharts
- Axios
- Vite

### Step 3: Start Development Server

```bash
npm run dev
```

**Expected Output:**

```
  ➜  Local:   http://localhost:3000/
  ➜  Press q to quit
```

**Visit:** http://localhost:3000

---

## 4️⃣ Verify Installation

### Backend Verification

```bash
# In the backend terminal
# Test endpoint
curl http://localhost:8000/

# Expected response
{
  "service": "DATA DOCTOR - Dataset Quality Inspector",
  "version": "1.0.0",
  "status": "active"
}
```

### Frontend Verification

```bash
# Navigate to http://localhost:3000 in your browser
# You should see the Data Doctor landing page
```

---

## 5️⃣ Docker Installation (Alternative)

### Prerequisite

- Install Docker Desktop from https://www.docker.com/

### Step 1: Navigate to Project Root

```bash
cd DataDoctor
```

### Step 2: Build and Run

```bash
docker-compose up --build
```

**Services:**

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Step 3: Stop Services

```bash
docker-compose down
```

---

## 🧪 Test with Sample Data

### Option 1: Using UI

1. Go to http://localhost:3000
2. Click "Upload Dataset"
3. Select `sample_data.csv` (provided in project root)
4. Enter target column: `default`
5. Enter sensitive features: `age`
6. Click "Analyze Dataset"

### Option 2: Using cURL

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -F "file=@sample_data.csv" \
  -F "target_column=default" \
  -F "sensitive_features=age"
```

### Option 3: Python Script

```python
import requests

with open('sample_data.csv', 'rb') as f:
    files = {'file': f}
    data = {
        'target_column': 'default',
        'sensitive_features': 'age'
    }
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files=files,
        data=data
    )
    print(response.json())
```

---

## 🔧 Troubleshooting

### Issue: Python not found

```bash
# Windows: Try python instead of python3
python --version

# macOS/Linux: Ensure Python3 installed
which python3
```

### Issue: pip modules fail to install

```bash
# Upgrade pip
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

```bash
# Use different port
uvicorn main:app --reload --port 8001

# Or find and kill process
# Linux/macOS:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Port 3000 already in use

```bash
# Edit vite.config.ts and change port
# Or kill process similar to above
```

### Issue: CORS errors in frontend

```bash
# Ensure backend CORS is enabled in main.py
# Or use proxy in vite.config.ts

# Already configured in provided code
```

### Issue: File upload fails

```bash
# Check file permissions
# Ensure /tmp directory exists
# Check disk space

# Windows users: Ensure temp folder path is accessible
```

---

## 📦 Development Setup

### Install Development Tools

```bash
# Backend
pip install pytest black flake8 mypy

# Frontend
npm install --save-dev @types/node
```

### Code Formatting

```bash
# Black (Python)
black backend/

# Prettier (JavaScript)
cd frontend && npx prettier --write src/
```

### Linting

```bash
# Python
flake8 backend/

# JavaScript
cd frontend && npm run lint
```

---

## 🚀 Production Deployment

### Using Docker Compose

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run production
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

**Backend:**

```bash
cd backend
source venv/bin/activate
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

**Frontend:**

```bash
cd frontend
npm run build
npm run preview
```

---

## 📊 Performance Optimization

### Backend

```python
# Enable uvicorn workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# Use production server (Gunicorn)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend

```bash
# Build optimized production bundle
npm run build

# Check bundle size
npm run build -- --analyze
```

---

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Enable HTTPS in production
- [ ] Set up firewall rules
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Add authentication/authorization
- [ ] Use environment variables for secrets
- [ ] Regular security updates

```bash
pip install -U pip setuptools wheel
```

---

## 📚 Next Steps

1. **Upload your first dataset** - Try with `sample_data.csv`
2. **Explore the dashboard** - Check all analysis tabs
3. **Review recommendations** - Follow suggested improvements
4. **Read API docs** - Visit http://localhost:8000/docs
5. **Check logs** - Monitor terminal output for errors

---

## 📞 Support

### Common Commands

```bash
# Check Python version
python --version

# Check Node version
node --version

# Verify virtual environment activated
which python  # Should show venv path

# Deactivate virtual environment
deactivate

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf frontend/node_modules
npm install --prefix frontend
```

---

## ✅ Installation Complete!

You're all set to use Data Doctor! 🎉

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

**Happy analyzing!** 🏥
