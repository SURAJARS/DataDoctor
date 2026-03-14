# Data Doctor 🏥 - Dataset Quality Inspector

**Production-Grade Dataset Quality Analysis Tool**

Detect ALL possible defects in your datasets that could break your machine learning pipeline.

---

## 🚀 Features

### Comprehensive Analysis (45+ Quality Checks)

- ✅ Missing Values Analysis
- ✅ Duplicate Rows & Columns
- ✅ Class Imbalance Detection
- ✅ Data Leakage Detection
- ✅ Feature Correlation Analysis
- ✅ Multicollinearity Detection
- ✅ Outlier Detection (Z-score, IQR, Isolation Forest)
- ✅ Distribution Analysis (Skewness, Kurtosis)
- ✅ Distribution Shift Detection (KS test)
- ✅ Cardinality Analysis
- ✅ Constant Feature Detection
- ✅ Feature Scaling Problems
- ✅ Data Drift Detection
- ✅ Rare Category Detection

### Advanced Features

- 📊 **Dataset Health Score** (0-100)
- 🎯 **ML Readiness Score** with actionable recommendations
- 🔧 **Auto Feature Engineering Suggestions**
- 🔍 **Bias Detection** (demographic, representation, measurement)
- ⚡ **Feature Importance** ranking
- 🛠️ **Data Cleaning Recommendations** with Python code
- 📈 **Feature Engineering Advisor**
- 🚀 **Large Dataset Support** (streaming/chunking)

### Supported Formats

- CSV
- Excel (.xlsx)
- Parquet
- JSON

### Large Dataset Support

- Small datasets (<50MB) - Full analysis
- Medium datasets (<500MB) - Optimized processing
- Large datasets (>500MB) - Streaming with chunking
- Automatic fallback to sampling for very large files

---

## 📋 Project Structure

```
DataDoctor/
├── backend/
│   ├── main.py                          # FastAPI server
│   ├── dataset_analyzer.py              # Core analysis engine
│   ├── scoring_engine.py                # Health scoring
│   ├── large_dataset_processor.py       # Large file handling
│   ├── ml_readiness_engine.py           # ML readiness evaluation
│   ├── feature_engineering_advisor.py   # Feature recommendations
│   ├── feature_importance_engine.py     # Feature ranking
│   ├── bias_detector.py                 # Bias detection
│   ├── data_cleaner.py                  # Cleaning recommendations
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx              # Landing page
│   │   │   └── Upload.tsx               # Dataset upload
│   │   ├── components/
│   │   │   └── Dashboard.tsx            # Analysis dashboard
│   │   ├── utils/
│   │   │   └── api.ts                   # API client
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── index.html
│
├── README.md
└── docker-compose.yml
```

---

## 🔧 Installation & Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## 📊 API Endpoints

### Analysis

- **POST** `/api/analyze` - Upload dataset and analyze
  - Parameters: `file`, `target_column` (optional), `sensitive_features` (optional)
  - Returns: `analysis_id`, summary scores

### Reports

- **GET** `/api/report/{analysis_id}` - Get complete analysis report
- **GET** `/api/summary/{analysis_id}` - Get executive summary

### Detailed Analysis

- **GET** `/api/health-score/{analysis_id}` - Dataset health score
- **GET** `/api/ml-readiness/{analysis_id}` - ML readiness assessment
- **GET** `/api/feature-engineering/{analysis_id}` - Feature engineering recommendations
- **GET** `/api/bias-detection/{analysis_id}` - Bias analysis results
- **GET** `/api/data-cleaning/{analysis_id}` - Data cleaning recommendations
- **GET** `/api/feature-importance/{analysis_id}` - Feature importance rankings

### Filtered Results

- **GET** `/api/issues/{analysis_id}` - Get issues (with optional severity filter)
- **GET** `/api/recommendations/{analysis_id}` - Get all recommendations

---

## 📈 Example Analysis Report

```json
{
  "analysis_id": "analysis_1234567890",
  "timestamp": "2024-03-12T10:30:00",
  "dataset_health_score": 72,
  "ml_readiness_score": 78,
  "overall_status": "Good",
  "dataset_info": {
    "rows": 50000,
    "columns": 25,
    "file_size_mb": 45.2,
    "file_type": "csv"
  },
  "health_score": {
    "dataset_health_score": 72,
    "overall_status": "Good",
    "critical_issues": [],
    "warnings": [
      {
        "severity": "high",
        "type": "missing_values",
        "description": "Column 'income' has 34% missing values"
      },
      {
        "severity": "medium",
        "type": "class_imbalance",
        "description": "Target variable has 85:15 class ratio"
      }
    ]
  },
  "ml_readiness": {
    "ml_readiness_score": 78,
    "readiness_status": "MOSTLY_READY",
    "critical_blockers": [],
    "recommendations": [
      "Implement imputation strategy for missing values",
      "Use SMOTE or class weights to address class imbalance"
    ]
  },
  "feature_engineering": {
    "recommendations": [
      {
        "category": "Missing Value Handling",
        "priority": "Critical",
        "recommendation": "Impute missing values",
        "code_snippet": "df.fillna(df.mean())"
      }
    ]
  },
  "bias_analysis": {
    "bias_risk_level": "Medium",
    "bias_findings": [
      {
        "type": "Class Imbalance",
        "severity": "High",
        "description": "Majority class represents 85% of data"
      }
    ]
  },
  "cleaning_recommendations": {
    "cleaning_steps": [
      {
        "action": "Remove duplicate rows",
        "priority": "High",
        "code": "df = df.drop_duplicates()"
      }
    ],
    "estimated_time": "Moderate (5-15 minutes)"
  },
  "feature_importance": {
    "top_features": [
      {
        "feature": "age",
        "importance": 0.23,
        "rank": 1
      }
    ]
  }
}
```

---

## 🎯 Dataset Health Score Breakdown

Score calculation considers:

| Factor                      | Impact  | Weight |
| --------------------------- | ------- | ------ |
| Missing Values              | 0-30pts | 30%    |
| Duplicates                  | 0-15pts | 15%    |
| Class Imbalance             | 0-15pts | 15%    |
| Outliers                    | 0-12pts | 12%    |
| Multicollinearity           | 0-15pts | 15%    |
| Constant/Redundant Features | 0-10pts | 10%    |
| Data Drift                  | 0-8pts  | 8%     |
| Data Type Issues            | 0-5pts  | 5%     |

---

## 🤖 ML Readiness Score

Considers:

- Dataset size (minimum 100 samples, ideal 1000+)
- Feature count (minimum 2, ideal 10+)
- Target variable quality and class balance
- Missing data percentage
- Feature distributions and relationships
- Data quality issues

**Status Levels:**

- 🔴 **NOT_READY** - Critical issues blocking training
- 🟡 **NEEDS_PREPARATION** - Extensive cleaning required
- 🟠 **MOSTLY_READY** - Some issues to address
- 🟢 **READY** - Good to train

---

## 🔍 Bias Detection

Detects multiple types of bias:

1. **Class Imbalance Bias** - Skewed target distribution
2. **Demographic Bias** - Different model outcomes across groups
3. **Representation Bias** - Underrepresented demographic groups
4. **Measurement Bias** - Data quality variations by group
5. **Selection Bias** - Artificial data constraints

---

## 🛠️ Quick Start Example

```python
import requests
import json

# Upload and analyze dataset
with open('my_dataset.csv', 'rb') as f:
    files = {'file': f}
    data = {
        'target_column': 'target',
        'sensitive_features': 'age,gender,race'
    }
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files=files,
        data=data
    )

analysis_id = response.json()['analysis_id']

# Get full report
report = requests.get(
    f'http://localhost:8000/api/report/{analysis_id}'
).json()

print(f"Health Score: {report['health_score']['dataset_health_score']}")
print(f"ML Readiness: {report['ml_readiness']['ml_readiness_score']}")
print(f"Critical Issues: {len(report['health_score']['critical_issues'])}")
```

---

## 📊 Dashboard Features

### Overview Tab

- Dataset health score with color-coded status
- ML readiness score and recommendations
- Dataset statistics (rows, columns, size)
- Key findings summary

### Issues Tab

- All detected issues color-coded by severity
- Issue descriptions and impacts
- Severity levels: Critical, High, Medium, Low

### ML Readiness Tab

- Training difficulty assessment
- Critical blockers and warnings
- Actionable recommendations
- Effort estimation

### Features Tab

- Feature importance rankings
- Top predictive features
- Feature correlation analysis

### Bias Tab

- Bias risk assessment
- Detected bias findings
- Mitigation strategies
- Fairness recommendations

### Recommendations Tab

- Prioritized action items
- Data cleaning steps with code
- Feature engineering suggestions
- Cleaning effort estimation

---

## 🚀 Performance Requirements Met

✅ Handles large datasets efficiently (streaming/chunking)
✅ Avoids memory crashes on 500MB+ files
✅ Uses parallel computation where possible
✅ Provides meaningful diagnostics
✅ Never skips any analysis
✅ Gives actionable recommendations

---

## 📦 Tech Stack

### Backend

- FastAPI (async web framework)
- Pandas (data manipulation)
- NumPy (numerical computing)
- Dask (large dataset processing)
- Scikit-learn (ML utilities)
- SciPy (statistical analysis)
- Plotly (visualization)

### Frontend

- React 18 (UI framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Recharts (visualizations)
- Axios (HTTP client)
- Vite (build tool)

---

## 📝 Constants & Thresholds

### Missing Values

- Critical: >50%
- High: >30%
- Medium: >10%
- Low: >5%

### Duplicates

- High: >20%
- Medium: >5%

### Class Imbalance

- Severe: >3:1 ratio
- Moderate: >1.5:1 ratio

### Outliers

- Detection: IQR method (Q1-1.5×IQR, Q3+1.5×IQR)
- Z-score: ±3σ
- Flagged if >1% of data

### Correlation

- High correlation: >0.9

### Cardinality

- High cardinality: >90% unique values

---

## 🔐 Security Considerations

- File size limits (recommend <2GB)
- Virus scanning recommended for production
- Input sanitization for database use
- User authentication (optional in current version)
- Rate limiting recommended
- HTTPS recommended for production

---

## 📚 Documentation

- API Documentation: `/docs` (Swagger UI)
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- Database integration for result persistence
- User authentication & authorization
- Advanced visualization dashboards
- Real-time streaming analysis
- Custom rule configuration
- API rate limiting

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎓 Built For

- **Data Scientists** - Ensure data quality before modeling
- **ML Engineers** - Automate dataset validation
- **Data Engineers** - Quality assurance pipelines
- **Analytics Teams** - Dataset profiling
- **SaaS Platforms** - Embedded quality assessment

---

## 🐛 Known Limitations

- In-memory caching (add database for persistence)
- No user authentication (add for multi-user)
- Limited historical tracking
- Sampling for extremely large files (>10GB)

---

## 🚀 Roadmap

- [ ] Database persistence
- [ ] User authentication
- [ ] Scheduled analysis jobs
- [ ] Alert system for regressions
- [ ] Data profiling API
- [ ] Custom rule engine
- [ ] Advanced visualizations
- [ ] SaaS multi-tenancy
- [ ] Data versioning
- [ ] Automated retraining triggers

---

**Questions? Issues? Reach out!**

Data Doctor - Making datasets ML-ready since 2024 🏥
