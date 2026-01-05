# API URLs and Endpoints Reference

## 🚀 Base URL

When running locally:
```
http://localhost:8000
```

When deployed (replace with your domain):
```
https://your-domain.com
```

---

## 📋 Available Endpoints

### 1. **Frontend Pages**

#### Main Application (Decision Tree Engine)
```
GET http://localhost:8000/
```
- **Description**: Main frontend page with Decision Tree Engine UI
- **Response**: HTML page with upload form and analysis interface
- **Usage**: Open in browser to use the application

#### Original Frontend
```
GET http://localhost:8000/original
```
- **Description**: Original frontend page (standard analysis)
- **Response**: HTML page with original analysis interface

#### Health Check
```
GET http://localhost:8000/health
```
- **Description**: Check if API is running
- **Response**: 
```json
{
  "status": "ok",
  "message": "API is running"
}
```

---

### 2. **Analysis Endpoints**

#### Decision Tree Engine (Recommended) ⭐
```
POST http://localhost:8000/analyze-decision-tree
```
- **Description**: AI Business Rules & Decision Tree Engine
  - Uses ML algorithms for pattern recognition
  - Applies explicit IF-ELSE business rules
  - Provides step-by-step explanations
  
- **Parameters**:
  - `file` (multipart/form-data): CSV/XLS/XLSX file
  - `use_ml` (query parameter, optional): `true` or `false` (default: `true`)

- **Example Request (cURL)**:
```bash
curl -X POST "http://localhost:8000/analyze-decision-tree?use_ml=true" \
  -F "file=@employee_data.csv"
```

- **Example Request (Python)**:
```python
import requests

url = "http://localhost:8000/analyze-decision-tree"
files = {"file": open("employee_data.csv", "rb")}
params = {"use_ml": "true"}

response = requests.post(url, files=files, params=params)
result = response.json()
```

- **Response Format**:
```json
{
  "detected_purpose": "Employee Analysis",
  "purpose_confidence": "High",
  "matched_keywords": ["employee_id", "employee"],
  "ml_pattern_recognition": {
    "ml_discovered_rules": [...],
    "feature_importance": {...},
    "apriori_patterns": [...]
  },
  "applied_rules": {
    "total_records_analyzed": 100,
    "total_rules_applied": 250,
    "average_rules_per_record": 2.5,
    "record_analyses": [...]
  },
  "final_decisions_summary": {...},
  "confidence_level": "High",
  "column_mapping": {...},
  "business_rules_applied": [...],
  "step_by_step_reasoning": [...]
}
```

#### Standard Analysis
```
POST http://localhost:8000/analyze
```
- **Description**: Original business rule discovery analysis
- **Parameters**:
  - `file` (multipart/form-data): CSV/XLS/XLSX file

- **Example Request**:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@employee_data.csv"
```

#### HR Analysis (Enhanced)
```
POST http://localhost:8000/analyze-hr
```
- **Description**: Enhanced HR analysis with ML-based rule discovery
- **Parameters**:
  - `file` (multipart/form-data): CSV/XLS/XLSX file
  - `prediction_input` (optional, JSON body): Input data for prediction

- **Example Request**:
```bash
curl -X POST "http://localhost:8000/analyze-hr" \
  -F "file=@employee_data.csv" \
  -F "prediction_input={\"salary\":50000,\"rating\":4.2}"
```

---

### 3. **Prediction Endpoints**

#### Predict Outcome
```
POST http://localhost:8000/predict
```
- **Description**: Predict outcome for a single record using a previously analyzed dataset
- **Request Body** (JSON):
```json
{
  "dataset_id": "uuid-string",
  "input_data": {
    "salary": 50000,
    "rating": 4.2,
    "attendance": 95
  }
}
```

- **Example Request**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
    "input_data": {
      "salary": 50000,
      "rating": 4.2
    }
  }'
```

#### Get Dataset Info
```
GET http://localhost:8000/datasets/{dataset_id}
```
- **Description**: Get information about a stored dataset
- **Example**:
```bash
curl "http://localhost:8000/datasets/123e4567-e89b-12d3-a456-426614174000"
```

- **Response**:
```json
{
  "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
  "rows": 100,
  "columns": ["employee_id", "salary", "rating"],
  "column_types": {
    "employee_id": "object",
    "salary": "int64",
    "rating": "float64"
  }
}
```

---

## 📝 Quick Start Guide

### 1. Start the Server

```bash
cd ai_project
uvicorn app:app --reload
```

The server will start at: `http://localhost:8000`

### 2. Access the Frontend

Open your browser and navigate to:
```
http://localhost:8000
```

### 3. Use the API Directly

#### Python Example:
```python
import requests

# Upload and analyze with Decision Tree Engine
url = "http://localhost:8000/analyze-decision-tree"
files = {"file": open("hr_data.csv", "rb")}
params = {"use_ml": "true"}

response = requests.post(url, files=files, params=params)
result = response.json()

print(f"Purpose: {result['detected_purpose']}")
print(f"Confidence: {result['confidence_level']}")
```

#### JavaScript Example:
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:8000/analyze-decision-tree?use_ml=true", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log("Purpose:", data.detected_purpose);
  console.log("Confidence:", data.confidence_level);
});
```

---

## 🔧 API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI (Interactive)
```
http://localhost:8000/docs
```

### ReDoc (Alternative)
```
http://localhost:8000/redoc
```

---

## 📊 Static Files

Static files (CSS, JS, images) are served from:
```
http://localhost:8000/static/
```

Example:
- CSS: `http://localhost:8000/static/style.css`
- JS: `http://localhost:8000/static/script.js`

---

## 🌐 Production Deployment

For production, update the base URL in your frontend code:

1. **Update `script.js`**:
   - Change `http://127.0.0.1:8000` to your production domain
   - Or use relative URLs: `/analyze-decision-tree`

2. **CORS Configuration**:
   - Update `allow_origins` in `app.py` to your domain
   - Example: `allow_origins=["https://yourdomain.com"]`

3. **HTTPS**:
   - Use HTTPS in production
   - Update all URLs to use `https://`

---

## 📌 Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main frontend (Decision Tree Engine) |
| `/original` | GET | Original frontend |
| `/health` | GET | Health check |
| `/analyze-decision-tree` | POST | **Decision Tree Engine (Recommended)** |
| `/analyze` | POST | Standard analysis |
| `/analyze-hr` | POST | Enhanced HR analysis |
| `/predict` | POST | Predict outcome |
| `/datasets/{id}` | GET | Get dataset info |
| `/docs` | GET | API documentation (Swagger) |
| `/redoc` | GET | API documentation (ReDoc) |

---

## 💡 Tips

1. **Use Decision Tree Engine** (`/analyze-decision-tree`) for the best experience
2. **Enable ML** (`use_ml=true`) for pattern recognition
3. **Check `/health`** to verify server is running
4. **Use `/docs`** for interactive API testing
5. **Frontend automatically handles URLs** - no manual configuration needed

---

## 🆘 Troubleshooting

### Server not starting?
- Check if port 8000 is available
- Try: `uvicorn app:app --reload --port 8001`

### CORS errors?
- Check `allow_origins` in `app.py`
- Ensure frontend URL matches allowed origins

### File upload errors?
- Check file format (CSV/XLS/XLSX)
- Verify file is not empty
- Check file encoding (UTF-8 recommended)

