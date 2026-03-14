# Quick Start Guide - Data Doctor 🏥

Get up and running with Data Doctor in 5 minutes!

---

## ⚡ 5-Minute Quickstart

### 1. Clone/Download Project

```bash
cd DataDoctor
```

### 2. Install Dependencies (2 min)

**Terminal 1 - Backend:**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm install
```

### 3. Start Services (1 min)

**Terminal 1:**

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

**Terminal 2:**

```bash
cd frontend
npm run dev
```

### 4. Open in Browser (1 min)

```
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
```

### 5. Upload & Analyze (1 min)

1. Click "Upload Dataset"
2. Select `sample_data.csv`
3. Enter target column: `default`
4. Click "Analyze Dataset"
5. 🎉 View comprehensive analysis!

---

## 🗂️ What You Get

- ✅ Dataset Health Score (0-100)
- ✅ 45+ Quality Checks
- ✅ ML Readiness Assessment
- ✅ Feature Engineering Recommendations
- ✅ Bias Detection Report
- ✅ Data Cleaning Guide
- ✅ Feature Importance Rankings

---

## 📊 Example Analysis Report

```json
{
  "dataset_health_score": 72,
  "ml_readiness_score": 78,
  "overall_status": "Good",
  "issues_detected": [
    {
      "type": "missing_values",
      "severity": "high",
      "description": "Column 'age' has 5% missing values"
    }
  ],
  "recommendations": [
    "Implement imputation strategy",
    "Use SMOTE for class imbalance",
    "Drop constant features"
  ]
}
```

---

## 🚀 Docker Alternative (1 command)

```bash
docker-compose up
```

Then visit: http://localhost:3000

---

## 📖 Full Documentation

See `README.md` and `INSTALLATION_GUIDE.md` for complete details.

---

## ❓ Troubleshooting

| Issue             | Solution                                       |
| ----------------- | ---------------------------------------------- |
| Port 8000 in use  | Change to 8001: `uvicorn main:app --port 8001` |
| Python not found  | Use `python3` on macOS/Linux                   |
| npm modules error | Run `npm cache clean --force`                  |
| CORS errors       | Already configured ✓                           |

---

## ✨ Key Features

### Real-time Analysis

- Fast dataset processing
- Streaming for large files (500MB+)
- Instant quality scores

### Comprehensive Reports

- Missing values analysis
- Duplicate detection
- Outlier identification
- Class imbalance detection
- Feature correlation
- Data drift detection

### Actionable Recommendations

- Python code snippets
- Step-by-step cleaning guide
- Priority-ranked improvements
- Implementation time estimates

### Advanced Modules

- ML Readiness Score
- Feature Engineering Advisor
- Bias Detection
- Feature Importance Ranking

---

## 🎓 Next Steps

1. Upload your dataset
2. Review the analysis report
3. Follow recommendations
4. Clean and prepare data
5. Train your model!

---

## 🔗 Useful Links

- **API Documentation**: http://localhost:8000/docs
- **Backend Code**: `backend/`
- **Frontend Code**: `frontend/src/`
- **Sample Data**: `sample_data.csv`

---

**Let's make your datasets ML-ready!** 🏥
