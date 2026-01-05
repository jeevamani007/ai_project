# HR Prediction Engine - UI Guide

## Overview

The HR Prediction Engine now has a beautiful, modern UI that displays analysis results and allows you to make predictions.

## Accessing the UI

### Main HR Prediction UI (Recommended)
- URL: `http://localhost:8000/` (root)
- This is the new HR-focused interface with prediction capabilities

### Original Analyzer UI
- URL: `http://localhost:8000/original`
- This is the original business rules analyzer interface

## Features

### 1. Dataset Upload
- Upload CSV, XLS, or XLSX files
- Click "Analyze Dataset" to process your HR data
- The system will detect the HR domain and extract business rules

### 2. Analysis Results Display

The UI displays results in organized tabs:

#### Summary Tab
- Domain detection with confidence level
- Matched keywords from HR domain
- Dataset ID and model availability status
- Target column information (if available)

#### Business Rules Tab
- IF-THEN business rules discovered using Decision Tree
- Human-readable rule descriptions
- Rules are displayed in clear, understandable format

#### Features Tab
- **Numerical Features**: List of numeric columns
- **Categorical Features**: List of categorical columns  
- **Feature Importance**: Visual bars showing importance percentages
- Features sorted by importance (most important first)

#### Hidden Patterns Tab
- Association rules discovered using Apriori algorithm
- Patterns showing relationships between features
- Useful for identifying hidden correlations

### 3. Prediction Section

Once a dataset is analyzed and a model is available:

1. **Prediction Form**: 
   - Input fields are automatically generated based on important features
   - Enter values for numerical and categorical features
   - Fields are labeled clearly

2. **Make Prediction**:
   - Click "Predict" button
   - System uses Decision Tree + Random Forest to predict outcome
   - Results include:
     - **Predicted Outcome**: The predicted value/class
     - **Confidence Level**: Percentage confidence in the prediction
     - **Explanation**: Human-readable explanation of why this prediction was made
     - **Input Data**: Summary of the input values used

### 4. Visual Design

- **Modern Gradient Design**: Purple/blue gradient theme
- **Card-based Layout**: Clean, organized card layouts
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Elements**: Hover effects and smooth transitions
- **Color-coded Information**: 
  - Green for success/high confidence
  - Orange for medium confidence
  - Red for errors/low confidence
  - Purple/blue for primary actions

## Usage Workflow

1. **Upload Dataset**
   ```
   → Select your HR dataset file (CSV/XLS/XLSX)
   → Click "Analyze Dataset"
   → Wait for analysis to complete
   ```

2. **Review Analysis**
   ```
   → View Summary tab for overview
   → Check Business Rules tab for discovered rules
   → Review Features tab for feature importance
   → Explore Hidden Patterns tab for associations
   ```

3. **Make Predictions**
   ```
   → Fill in the prediction form with employee data
   → Click "Predict" button
   → Review prediction results with explanation
   ```

## API Endpoints Used

The UI uses these backend endpoints:
- `POST /analyze-hr` - Analyze HR dataset
- `POST /predict` - Make predictions on analyzed dataset
- `GET /datasets/{dataset_id}` - Get dataset information (not used in UI currently)

## Example Workflow

1. Upload an HR dataset with columns like:
   - attendance, late_days, leave_days, salary, performance_score, etc.

2. System analyzes and shows:
   - Detected domain: HR (High Confidence)
   - Business rules like: "IF attendance < 75 THEN RISK = HIGH"
   - Feature importance ranking

3. Enter prediction input:
   - attendance: 65
   - late_days: 6
   - leave_days: 8
   - salary: 50000

4. Get prediction:
   - Predicted Outcome: HIGH RISK
   - Confidence: 85.2%
   - Explanation: "Employee shows low attendance (65), high late_days (6), high leave_days (8). Predicted outcome is 'HIGH RISK' with 85.2% confidence."

## Tips

- **For Best Results**: Ensure your dataset has clear HR-related columns
- **Feature Names**: Use standard HR terminology (see .md file for keywords)
- **Prediction Accuracy**: More training data = better predictions
- **Missing Fields**: You don't need to fill all fields, but more data improves accuracy

## Troubleshooting

- **No Model Available**: Dataset may not have a target column for prediction. System will still show business rules.
- **Prediction Errors**: Ensure input data types match the original dataset (numbers vs text)
- **Empty Results**: Check that your dataset has sufficient data (at least 10 rows recommended)

