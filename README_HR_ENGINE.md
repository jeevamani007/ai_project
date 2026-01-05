# HR Business Rules and Prediction Engine

## Overview

This is an AI-powered Business Rules and Prediction Engine specialized in the HR domain. It analyzes HR datasets, discovers business rules using Machine Learning (Decision Tree, Random Forest, and Apriori algorithms), and provides predictions for employee risk/performance.

## Features

### 1. Domain Detection
- Analyzes uploaded datasets (CSV/XLS/XLSX)
- Detects HR domain based on column keywords from `.md` file
- Identifies key HR features (employee_id, attendance, late_days, leave_days, salary, performance_score, etc.)

### 2. Feature Extraction
- Lists important columns in the dataset
- Categorizes columns as numerical or categorical

### 3. Business Rules Discovery
- Generates clear IF-ELSE business rules using Decision Tree logic
- Uses Random Forest to improve accuracy and feature importance
- Identifies patterns using Apriori algorithm (hidden associations)
- Provides human-readable explanations for each rule
- Beginner-friendly language for HR personnel

### 4. Prediction
- Accepts new user input (single record with values for key features)
- Predicts outcome related to employee performance or risk (e.g., HIGH RISK / LOW RISK)
- Uses Decision Tree + Random Forest for accurate predictions
- Provides reasoning/explanation in simple language

## API Endpoints

### POST `/analyze-hr`
Enhanced HR analysis endpoint that returns output in the specified JSON format.

**Request:**
- File upload (CSV/XLS/XLSX)
- Optional: `prediction_input` as JSON string in request body

**Response Format:**
```json
{
  "detected_domain": "HR",
  "domain_confidence": "High",
  "keywords_matched": ["attendance", "late_days", "leave_days"],
  "important_features": {
    "numerical": ["attendance", "late_days", "leave_days", "salary", "performance_score"],
    "categorical": ["department", "designation", "employment_type"]
  },
  "business_rules": [
    "IF attendance < 75% THEN RISK = HIGH",
    "IF late_days > 5 THEN RISK = HIGH",
    "IF leave_days > 10 THEN REVIEW_REQUIRED = TRUE"
  ],
  "feature_importance": {
    "attendance": 45.0,
    "late_days": 35.0,
    "leave_days": 20.0
  },
  "hidden_patterns": [
    "Late_days > 5 AND leave_days > 10 → High Risk"
  ],
  "dataset_id": "uuid-here",
  "model_available": true,
  "target_column": "risk_level"
}
```

### POST `/predict`
Predict outcome for a single record using a previously analyzed dataset.

**Request:**
```json
{
  "dataset_id": "uuid-from-analyze-hr-response",
  "input_data": {
    "attendance": 65,
    "late_days": 6,
    "leave_days": 8,
    "salary": 50000
  }
}
```

**Response:**
```json
{
  "prediction_input": {
    "attendance": 65,
    "late_days": 6,
    "leave_days": 8,
    "salary": 50000
  },
  "predicted_outcome": "HIGH RISK",
  "prediction_explanation": "Employee shows low attendance (65), high late_days (6), high leave_days (8). Predicted outcome is 'HIGH RISK' with 85.2% confidence.",
  "confidence": 0.852,
  "feature_importance": {
    "attendance": 45.0,
    "late_days": 35.0,
    "leave_days": 20.0
  },
  "prediction_id": "pred_20240101_120000_123456"
}
```

### GET `/datasets/{dataset_id}`
Get information about a stored dataset.

### POST `/analyze`
Original analyze endpoint (returns detailed analysis in original format).

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the `.md` file is in the `ai_project` directory with HR keywords.

3. Run the server:
```bash
uvicorn app:app --reload
```

## Usage Example

### Python Example

```python
import requests

# 1. Analyze dataset
with open('hr_data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/analyze-hr', files=files)
    result = response.json()
    
    dataset_id = result['dataset_id']
    print(f"Detected domain: {result['detected_domain']}")
    print(f"Business rules: {result['business_rules']}")

# 2. Make prediction
prediction_data = {
    "dataset_id": dataset_id,
    "input_data": {
        "attendance": 65,
        "late_days": 6,
        "leave_days": 8,
        "salary": 50000
    }
}

response = requests.post('http://localhost:8000/predict', json=prediction_data)
prediction = response.json()
print(f"Predicted outcome: {prediction['predicted_outcome']}")
print(f"Explanation: {prediction['prediction_explanation']}")
```

## File Structure

```
ai_project/
├── app.py                 # FastAPI application with endpoints
├── analyzer.py            # Original business rules analyzer
├── hr_analyzer.py         # Enhanced HR analyzer (new JSON format)
├── ml_analyzer.py         # ML-based rule discovery (Decision Tree, Random Forest, Apriori)
├── keyword_loader.py      # Loads HR keywords from .md file
├── data_storage.py        # Stores datasets and models
├── .md                    # HR domain keywords list
├── requirements.txt       # Python dependencies
└── storage/               # Directory for stored datasets and predictions
```

## Key Components

### MLBusinessRulesEngine
- Trains Decision Tree and Random Forest models
- Extracts human-readable IF-ELSE rules
- Calculates feature importance
- Provides predictions with explanations

### Keyword Loader
- Parses `.md` file to extract HR keywords
- Matches dataset columns against keywords
- Enhances domain detection accuracy

### Data Storage
- Stores uploaded datasets (in-memory + CSV backup)
- Stores trained ML models
- Stores prediction history
- Provides dataset/model retrieval

## Notes

- The system prioritizes explainable rules over complex black-box logic
- Predictions are consistent with discovered business rules
- Confidence levels are provided where applicable
- Adapts dynamically to different HR datasets
- Supports both classification and regression predictions
- Apriori algorithm is optional (requires mlxtend package)

## Requirements

See `requirements.txt` for full list. Key dependencies:
- fastapi
- pandas
- scikit-learn
- numpy
- mlxtend (for Apriori algorithm)

