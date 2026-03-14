# Data Doctor API Reference Guide

Complete documentation of all API endpoints.

---

## 🔗 Base URL

```
Development: http://localhost:8000
Production: https://yourdomain.com
```

## 📚 API Version

```
Current Version: 1.0.0
Docs: /docs (Swagger UI)
ReDoc: /redoc
OpenAPI: /openapi.json
```

---

## 📤 POST Endpoints

### 1. Upload & Analyze Dataset

**Endpoint:** `POST /api/analyze`

**Purpose:** Upload a dataset and run comprehensive analysis

**Request:**

```
Method: POST
Content-Type: multipart/form-data

Parameters:
- file (File, required): The dataset file to analyze
- target_column (string, optional): Name of the target variable
- sensitive_features (string, optional): Comma-separated sensitive features
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -F "file=@dataset.csv" \
  -F "target_column=target" \
  -F "sensitive_features=age,gender,race"
```

**Response (201/202):**

```json
{
  "status": "success",
  "analysis_id": "analysis_1710228600",
  "summary": {
    "dataset_health_score": 72,
    "ml_readiness_score": 78,
    "overall_status": "Good",
    "critical_issues": 0,
    "total_warnings": 5
  },
  "report_url": "/api/report/analysis_1710228600"
}
```

**Error Responses:**

```json
{
  "status": "error",
  "detail": "Unsupported file type: .doc"
}
```

**Supported Formats:**

- `.csv` - Comma-separated values
- `.xlsx` - Excel spreadsheet
- `.parquet` - Apache Parquet
- `.json` - JSON format

**File Size Limits:**

- Soft limit: 2GB
- Recommended: <500MB
- Larger files use streaming/sampling

---

## 📥 GET Endpoints

### 2. Get Full Report

**Endpoint:** `GET /api/report/{analysis_id}`

**Purpose:** Retrieve complete analysis report

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/report/analysis_1710228600"
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "timestamp": "2024-03-12T10:30:00",
  "dataset_info": {
    "rows": 1000,
    "columns": 25,
    "file_size_mb": 4.5,
    "file_type": "csv"
  },
  "health_score": { ... },
  "ml_readiness": { ... },
  "analysis_details": { ... },
  "feature_engineering": { ... },
  "bias_analysis": { ... },
  "cleaning_recommendations": { ... },
  "feature_importance": { ... }
}
```

**Error Responses:**

```json
{
  "detail": "Analysis not found"
}
```

---

### 3. Get Executive Summary

**Endpoint:** `GET /api/summary/{analysis_id}`

**Purpose:** Get brief summary without full details

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/summary/analysis_1710228600"
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "timestamp": "2024-03-12T10:30:00",
  "dataset": {
    "rows": 1000,
    "columns": 25,
    "file_size_mb": 4.5
  },
  "health_score": 72,
  "health_status": "Good",
  "ml_readiness_score": 78,
  "ml_readiness_status": "MOSTLY_READY",
  "critical_blockers": [],
  "bias_risk_level": "Medium",
  "top_issues": [],
  "cleaning_effort": "Moderate (5-15 minutes)",
  "top_features": []
}
```

---

### 4. Get Health Score

**Endpoint:** `GET /api/health-score/{analysis_id}`

**Purpose:** Get dataset health score and details

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "health_score": {
    "dataset_health_score": 72,
    "score_breakdown": {
      "missing_values_impact": 30,
      "duplicates_impact": 15,
      "class_imbalance_impact": 15,
      "outliers_impact": 12,
      "multicollinearity_impact": 15,
      "redundant_features_impact": 10,
      "data_drift_impact": 8,
      "data_types_impact": 5
    },
    "critical_issues": [],
    "warnings": [
      {
        "severity": "high",
        "type": "missing_values",
        "description": "Column 'X' has 15% missing values"
      }
    ],
    "overall_status": "Good",
    "recommendation": "Dataset is mostly ready..."
  },
  "dataset_info": { ... }
}
```

---

### 5. Get ML Readiness

**Endpoint:** `GET /api/ml-readiness/{analysis_id}`

**Purpose:** Get ML training readiness assessment

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "ml_readiness": {
    "ml_readiness_score": 78,
    "readiness_status": "MOSTLY_READY",
    "critical_blockers": [],
    "warnings": [
      {
        "issue": "class_imbalance"
      }
    ],
    "recommendations": [
      "Use SMOTE for class imbalance",
      "Implement imputation strategy"
    ],
    "estimated_training_difficulty": {
      "difficulty_level": "Moderate",
      "factors": {
        "data_quality": "Good",
        "class_balance": "Imbalanced",
        "feature_quality": "Good"
      },
      "estimated_effort": "Medium (~3-4 hours)"
    }
  }
}
```

---

### 6. Get Feature Engineering Recommendations

**Endpoint:** `GET /api/feature-engineering/{analysis_id}`

**Purpose:** Get feature engineering suggestions

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "feature_engineering": {
    "recommendations": [
      {
        "category": "Encoding",
        "priority": "High",
        "issue": "Categorical column 'X'",
        "recommendation": "One-Hot Encoding",
        "affected_columns": ["col1", "col2"],
        "reason": "Most algorithms require numerical input",
        "code_snippet": "df = pd.get_dummies(df, columns=['col1'])"
      }
    ],
    "priority_ranking": [ ... ],
    "implementation_guide": "Step-by-step guide..."
  }
}
```

---

### 7. Get Bias Detection Results

**Endpoint:** `GET /api/bias-detection/{analysis_id}`

**Purpose:** Get bias and fairness analysis

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "bias_analysis": {
    "bias_findings": [
      {
        "type": "Class Imbalance",
        "severity": "High",
        "description": "Majority class: 85%",
        "impact": "Model biased towards majority class",
        "mitigation": "Use SMOTE or class weights"
      }
    ],
    "bias_risk_level": "Medium",
    "recommendations": [
      "Use fairness metrics for evaluation",
      "Apply bias-aware training"
    ]
  }
}
```

---

### 8. Get Data Cleaning Recommendations

**Endpoint:** `GET /api/data-cleaning/{analysis_id}`

**Purpose:** Get data cleaning recommendations with code

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "cleaning_recommendations": {
    "cleaning_steps": [
      {
        "category": "Missing Values",
        "priority": "High",
        "action": "Impute column 'X'",
        "reason": "15% missing values detected",
        "code": "df['X'].fillna(df['X'].median(), inplace=True)",
        "reversible": false
      }
    ],
    "estimated_time": "Moderate (5-15 minutes)",
    "implementation_commands": "#!/bin/bash\n... Python script ..."
  }
}
```

---

### 9. Get Feature Importance

**Endpoint:** `GET /api/feature-importance/{analysis_id}`

**Purpose:** Get feature importance rankings

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "feature_importance": {
    "status": "success",
    "importance_scores": {
      "feature_1": 0.28,
      "feature_2": 0.22,
      "feature_3": 0.15
    },
    "top_features": [
      {
        "feature": "feature_1",
        "importance": 0.28,
        "rank": 1
      }
    ],
    "model_type": "RandomForest",
    "accuracy": 0.85
  }
}
```

---

### 10. Get Issues List

**Endpoint:** `GET /api/issues/{analysis_id}`

**Purpose:** Get detected issues (with optional filtering)

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
Query Parameter: severity (string, optional)
  - Values: "critical", "high", "medium", "low"

Example: /api/issues/analysis_123?severity=critical
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "severity_filter": "high",
  "issues": [
    {
      "severity": "high",
      "type": "missing_values",
      "description": "Column 'X' has 15% missing values"
    }
  ],
  "issue_count": 2
}
```

---

### 11. Get Recommendations List

**Endpoint:** `GET /api/recommendations/{analysis_id}`

**Purpose:** Get all recommendations across all modules

**Request:**

```
Method: GET
Path Parameter: analysis_id (string, required)
```

**Response (200):**

```json
{
  "analysis_id": "analysis_1710228600",
  "recommendations": {
    "health_recommendations": "Dataset is mostly ready...",
    "ml_recommendations": [
      "Implement imputation strategy...",
      "Use SMOTE for class imbalance..."
    ],
    "feature_engineering": [
      {
        "priority": "High",
        "recommendation": "One-Hot Encoding for categorical features"
      }
    ],
    "cleaning_steps": [
      {
        "priority": "High",
        "action": "Impute missing values"
      }
    ],
    "bias_mitigation": ["Apply fairness constraints..."]
  }
}
```

---

### 12. Get All Endpoints

**Endpoint:** `GET /`

**Purpose:** Get list of all available endpoints

**Response (200):**

```json
{
  "service": "DATA DOCTOR - Dataset Quality Inspector",
  "version": "1.0.0",
  "status": "active",
  "endpoints": {
    "upload": "/api/analyze",
    "health_score": "/api/health-score/{analysis_id}",
    "ml_readiness": "/api/ml-readiness/{analysis_id}",
    "feature_engineering": "/api/feature-engineering/{analysis_id}",
    "bias_detection": "/api/bias-detection/{analysis_id}",
    "data_cleaning": "/api/data-cleaning/{analysis_id}"
  }
}
```

---

## 🔐 Request Headers

### Required (Optional but Recommended)

```
Content-Type: application/json          (for JSON responses)
Content-Type: multipart/form-data       (for file uploads)
Accept: application/json
```

### Optional

```
X-Request-ID: unique-id-for-tracking
X-API-Key: your-api-key               (if authentication enabled)
```

---

## 📊 Response Formats

### Success Response

```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2024-03-12T10:30:00Z",
    "version": "1.0.0"
  }
}
```

### Error Response

```json
{
  "status": "error",
  "detail": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

### Supported Status Codes

```
200 OK              - Request successful
201 Created         - Resource created
202 Accepted        - Request accepted (async)
400 Bad Request     - Invalid request
404 Not Found       - Resource not found
422 Unprocessable   - Validation error
500 Server Error    - Internal error
```

---

## 🔌 Request/Response Examples

### Example 1: Upload and Analyze CSV

**Request:**

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@data.csv" \
  -F "target_column=target" \
  -F "sensitive_features=age"
```

**Response:**

```json
{
  "status": "success",
  "analysis_id": "analysis_1710228600",
  "summary": {
    "dataset_health_score": 72,
    "ml_readiness_score": 78,
    "overall_status": "Good",
    "critical_issues": 0,
    "total_warnings": 5
  }
}
```

### Example 2: Get Full Report

**Request:**

```bash
curl -X GET "http://localhost:8000/api/report/analysis_1710228600"
```

**Response:**

```json
{
  "analysis_id": "analysis_1710228600",
  "health_score": { ... },
  "ml_readiness": { ... },
  ...
}
```

### Example 3: Filter Issues by Severity

**Request:**

```bash
curl -X GET "http://localhost:8000/api/issues/analysis_1710228600?severity=critical"
```

**Response:**

```json
{
  "analysis_id": "analysis_1710228600",
  "severity_filter": "critical",
  "issues": [ ... ],
  "issue_count": 0
}
```

---

## 🛠️ Python Client Examples

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Upload and analyze
with open('dataset.csv', 'rb') as f:
    files = {'file': f}
    data = {
        'target_column': 'target',
        'sensitive_features': 'age,gender'
    }
    response = requests.post(f"{BASE_URL}/api/analyze", files=files, data=data)
    result = response.json()
    analysis_id = result['analysis_id']

# 2. Get full report
response = requests.get(f"{BASE_URL}/api/report/{analysis_id}")
report = response.json()

# 3. Get health score
response = requests.get(f"{BASE_URL}/api/health-score/{analysis_id}")
health = response.json()

# 4. Get recommendations
response = requests.get(f"{BASE_URL}/api/recommendations/{analysis_id}")
recommendations = response.json()

# 5. Filter issues
response = requests.get(f"{BASE_URL}/api/issues/{analysis_id}?severity=critical")
critical_issues = response.json()
```

---

## 🌐 JavaScript/TypeScript Client Examples

```typescript
const BASE_URL = "http://localhost:8000";

// 1. Upload and analyze
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("target_column", "target");
formData.append("sensitive_features", "age,gender");

const response = await fetch(`${BASE_URL}/api/analyze`, {
  method: "POST",
  body: formData,
});
const data = await response.json();
const analysisId = data.analysis_id;

// 2. Get full report
const report = await fetch(`${BASE_URL}/api/report/${analysisId}`);
const reportData = await report.json();

// 3. Get health score
const health = await fetch(`${BASE_URL}/api/health-score/${analysisId}`);
const healthData = await health.json();

// 4. Get recommendations
const recommendations = await fetch(
  `${BASE_URL}/api/recommendations/${analysisId}`,
);
const recData = await recommendations.json();
```

---

## ⏱️ Typical API Flow

```
1. POST /api/analyze
   ↓
   (File uploaded and analysis started)
   ↓
2. GET /api/report/{id}
   ↓
   (Full analysis results)
   ↓
3. GET /api/health-score/{id}
   GET /api/ml-readiness/{id}
   GET /api/feature-engineering/{id}
   GET /api/bias-detection/{id}
   GET /api/data-cleaning/{id}
   GET /api/feature-importance/{id}
   ↓
   (Specific module results)
```

---

## 🔍 Swagger Documentation

**Live API Documentation:**

```
http://localhost:8000/docs
```

**ReDoc Documentation:**

```
http://localhost:8000/redoc
```

**OpenAPI Schema:**

```
http://localhost:8000/openapi.json
```

---

## ⚠️ Error Handling

### Common Error Codes

```
UNSUPPORTED_FILE_TYPE
- Message: "Unsupported file type: .xyz"
- Solution: Use CSV, Excel, Parquet, or JSON

FILE_TOO_LARGE
- Message: "File exceeds size limit"
- Solution: Split into smaller files

ANALYSIS_NOT_FOUND
- Message: "Analysis not found"
- Solution: Verify analysis_id is correct

MISSING_TARGET_COLUMN
- Message: "Target column not found"
- Solution: Specify correct target_column name

INVALID_REQUEST
- Message: "Invalid request parameters"
- Solution: Check request format and parameter types
```

---

## 🔒 Rate Limiting (Optional)

When implemented:

```
X-RateLimit-Limit: 1000        (requests per hour)
X-RateLimit-Remaining: 999     (requests remaining)
X-RateLimit-Reset: 1710232800  (reset timestamp)
```

---

## 📋 API Versioning

Current Version: `1.0.0`

Future versions will be available at:

```
/api/v2/analyze
/api/v2/report/{id}
```

---

## 🚀 Best Practices

### Do's ✅

- Use analysis_id for subsequent requests
- Check response status codes
- Handle errors gracefully
- Cache analysis results
- Use appropriate severity filters
- Make requests sequentially

### Don'ts ❌

- Don't reupload same file repeatedly
- Don't ignore error responses
- Don't use invalid file types
- Don't upload files >2GB
- Don't make rapid repeated requests

---

## 🔗 Related Resources

- **Backend Code**: `backend/main.py`
- **Full Documentation**: `README.md`
- **Quick Start**: `QUICKSTART.md`
- **Installation Guide**: `INSTALLATION_GUIDE.md`

---

**Data Doctor API Reference v1.0.0**
**Last Updated:** March 12, 2024
