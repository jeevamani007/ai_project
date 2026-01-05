# AI Business Rules & Decision Tree Engine

## Overview

The Decision Tree Engine is a comprehensive HR data analysis system that combines:
1. **ML Pattern Recognition** - Uses machine learning algorithms (Decision Trees, Random Forest, Apriori) to discover patterns
2. **Explicit Business Rules** - Applies transparent IF-ELSE decision tree rules based on HR policies
3. **Purpose Detection** - Automatically identifies the purpose of the dataset using keywords
4. **Transparent Reasoning** - Provides step-by-step explanations for all decisions

## Features

### Purpose Detection Rules

The engine automatically detects the purpose of your data:

- **Employee Analysis**: Detects `employee_id`, `employee`, `staff`
- **Salary Analysis**: Detects `salary`, `payroll`, `ctc`
- **Attendance Analysis**: Detects `punch_in`, `punch_out`, `attendance`
- **Leave Analysis**: Detects `leave`, `leave_type`, `lop`
- **Performance Analysis**: Detects `rating`, `performance`, `appraisal`

### Decision Tree Business Rules

#### 1. Employee → Salary Level
```
IF salary >= 80000 → Salary_Level = High
ELSE IF salary >= 40000 → Salary_Level = Medium
ELSE → Salary_Level = Low
```

#### 2. Attendance → Time Check
```
IF punch_in <= office_start_time → Status = On Time
ELSE → Status = Late
```

#### 3. Attendance → Exit Check
```
IF punch_out >= office_end_time → Exit = Full Day
ELSE → Exit = Early Exit
```

#### 4. Working Hours
```
IF working_hours >= 8 → Day_Status = Full Day
ELSE IF working_hours >= 4 → Day_Status = Half Day
ELSE → Day_Status = Absent
```

#### 5. Leave Decision
```
IF leave_type = Casual AND leave_days <= 2 → Leave_Status = Approved
ELSE IF leave_type = Sick AND medical_proof = Yes → Leave_Status = Approved
ELSE → Leave_Status = Rejected

IF leave_type = LOP → Salary_Deduction = Yes
```

#### 6. Performance Rating
```
IF rating >= 4.5 → Performance = Excellent
ELSE IF rating >= 3 → Performance = Good
ELSE → Performance = Needs Improvement
```

#### 7. Increment Decision
```
IF Performance = Excellent → Increment = 20%
ELSE IF Performance = Good → Increment = 10%
ELSE → Increment = 0%
```

#### 8. Final Employee Status
```
IF attendance_good AND performance_good AND no_disciplinary_issues
→ Employee_Status = Active
ELSE
→ Employee_Status = Review Required
```

## API Usage

### Endpoint: `/analyze-decision-tree`

**Method**: POST

**Request**:
- `file`: CSV/XLS/XLSX file (multipart/form-data)
- `use_ml`: boolean (optional, default: true) - Enable ML pattern recognition

**Response Format**:
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
  "final_decisions_summary": {
    "Salary_Level": {...},
    "Performance": {...}
  },
  "confidence_level": "High",
  "column_mapping": {...},
  "business_rules_applied": [...],
  "step_by_step_reasoning": [...]
}
```

### Example Request (cURL)

```bash
curl -X POST "http://localhost:8000/analyze-decision-tree" \
  -F "file=@employee_data.csv" \
  -F "use_ml=true"
```

### Example Request (Python)

```python
import requests

url = "http://localhost:8000/analyze-decision-tree"
files = {"file": open("employee_data.csv", "rb")}
data = {"use_ml": "true"}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Detected Purpose: {result['detected_purpose']}")
print(f"Confidence Level: {result['confidence_level']}")
print(f"Applied Rules: {result['applied_rules']['total_rules_applied']}")
```

## Output Format

The engine provides:

1. **Detected Purpose**: What type of HR analysis this is
2. **Applied Rules**: Step-by-step rules applied to each record
3. **Final Decision**: Summary of all decisions made
4. **Confidence Level**: High / Medium / Low based on rule coverage

## How It Works

### Step 1: Purpose Detection
- Scans column names for keywords
- Matches against known HR domain keywords
- Assigns purpose with confidence level

### Step 2: ML Pattern Recognition (if enabled)
- Uses Decision Tree and Random Forest algorithms
- Discovers hidden patterns in data
- Identifies feature importance
- Finds association rules using Apriori algorithm

### Step 3: Column Mapping
- Automatically maps business rule fields to actual column names
- Handles variations in column naming (e.g., "punch_in" vs "check_in")

### Step 4: Business Rules Application
- Applies relevant IF-ELSE rules based on detected purpose
- Processes each record through decision tree
- Generates explanations for each decision

### Step 5: Final Summary
- Aggregates decisions across all records
- Calculates confidence level
- Provides distribution of outcomes

## Important Notes

- **No Guessing**: Uses only given columns and values
- **Transparent Logic**: All rules are explainable
- **Decision Tree Style**: Uses IF-ELSE reasoning
- **ML + Rules**: Combines pattern recognition with explicit logic
- **User-Friendly**: Output in simple, understandable English

## File Structure

```
ai_project/
├── decision_tree_engine.py    # Main decision tree engine
├── app.py                      # FastAPI endpoints
├── ml_analyzer.py              # ML pattern recognition
├── keyword_loader.py           # Keyword matching
└── analyzer.py                 # Domain detection
```

## Requirements

- pandas
- numpy
- scikit-learn
- fastapi
- mlxtend (for Apriori algorithm)

## Example Output Explanation

For a record with:
- `salary = 50000`
- `punch_in = "09:30"`
- `working_hours = 8.5`
- `rating = 4.2`

The engine will:

1. **Detect Purpose**: "Employee Analysis" (based on employee_id column)
2. **Apply Salary Rule**: "Salary 50000 is >= 40000 but < 80000, so Salary Level is Medium"
3. **Apply Attendance Rule**: "Punch-in time 09:30 is > office start time 09:00, so Status is Late"
4. **Apply Working Hours Rule**: "Working hours 8.5 is >= 8, so Day Status is Full Day"
5. **Apply Performance Rule**: "Rating 4.2 is >= 3.0 but < 4.5, so Performance is Good"
6. **Apply Increment Rule**: "Since Performance is Good, Increment is 10%"
7. **Final Status**: "Employee has attendance issues, so Employee Status is Review Required"

All with step-by-step explanations and confidence levels!

