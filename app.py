from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import pandas as pd
from io import BytesIO
from analyzer import analyze_data
from hr_analyzer import analyze_hr_dataset, predict_hr_outcome, analyze_and_predict_combined
from decision_tree_engine import analyze_hr_with_decision_tree
from prediction_engine import analyze_with_prediction_engine
from data_storage import storage
from csv_parser import parse_csv_robust
import os
import uuid

app = FastAPI(title="Business Rules Analyst AI")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for frontend assets
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    """Serve the HR Prediction Engine frontend HTML file"""
    hr_frontend_file = os.path.join(frontend_path, "hr_index.html")
    if os.path.exists(hr_frontend_file):
        return FileResponse(hr_frontend_file)
    
    # Fallback to original frontend
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Frontend not found. Please ensure frontend/hr_index.html exists."}

@app.get("/original")
async def original_frontend():
    """Serve the original frontend HTML file"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Frontend not found. Please ensure frontend/index.html exists."}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}

class PredictionInput(BaseModel):
    dataset_id: str
    input_data: Dict[str, Any]

class AnalyzeWithPredictionInput(BaseModel):
    input_data: Optional[Dict[str, Any]] = None

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Original analyze endpoint - returns detailed analysis"""
    try:
        # Read file content
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Load dataframe based on file type
        df = None
        if file_extension == 'csv':
            try:
                df = parse_csv_robust(contents)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}. Please check your CSV file format.")
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(BytesIO(contents))
        elif file_extension == 'sql':
            raise HTTPException(status_code=400, detail="SQL file execution requires database connection. Please export to CSV/XLSX first.")
        else:
            try:
                df = parse_csv_robust(contents)
            except:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. Supported formats: CSV, XLS, XLSX")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        result = analyze_data(df)
        return result
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded file is empty or invalid")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/analyze-hr")
async def analyze_hr(file: UploadFile = File(...), prediction_input: Optional[str] = Body(None, embed=True)):
    """
    Enhanced HR analysis endpoint - Returns output in specified JSON format
    Optionally accepts prediction input data
    """
    try:
        # Read file content
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Load dataframe
        df = None
        if file_extension == 'csv':
            try:
                df = parse_csv_robust(contents)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}. Please check your CSV file format.")
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(BytesIO(contents))
        else:
            try:
                df = parse_csv_robust(contents)
            except:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. Supported formats: CSV, XLS, XLSX")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Generate dataset ID and store
        dataset_id = str(uuid.uuid4())
        storage.store_dataset(dataset_id, df)
        
        # Parse prediction input if provided
        input_data = None
        if prediction_input:
            import json
            try:
                input_data = json.loads(prediction_input) if isinstance(prediction_input, str) else prediction_input
            except:
                pass
        
        # Analyze dataset
        result = analyze_hr_dataset(df, dataset_id)
        
        # Add prediction if input_data provided
        if input_data:
            prediction_result = predict_hr_outcome(dataset_id, input_data)
            if "error" not in prediction_result:
                result["prediction_input"] = prediction_result.get("prediction_input")
                result["predicted_outcome"] = prediction_result.get("predicted_outcome")
                result["prediction_explanation"] = prediction_result.get("prediction_explanation")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/predict")
async def predict(prediction_input: PredictionInput):
    """
    Predict outcome for a single record using a previously analyzed dataset
    """
    try:
        result = predict_hr_outcome(prediction_input.dataset_id, prediction_input.input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/datasets/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    """Get information about a stored dataset"""
    df = storage.get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": df.columns.tolist(),
        "column_types": {col: str(df[col].dtype) for col in df.columns}
    }

@app.post("/analyze-prediction")
async def analyze_prediction(file: UploadFile = File(...)):
    """
    Comprehensive HR Prediction Engine
    - Reads full data first
    - Matches all HR keywords
    - Applies category-specific business rules
    - Shows predictions with person names and full data
    """
    try:
        # Read file content
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Load dataframe
        df = None
        if file_extension == 'csv':
            try:
                df = parse_csv_robust(contents)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}. Please check your CSV file format.")
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(BytesIO(contents))
        else:
            try:
                df = parse_csv_robust(contents)
            except:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. Supported formats: CSV, XLS, XLSX")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Analyze using Prediction Engine
        result = analyze_with_prediction_engine(df)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/analyze-decision-tree")
async def analyze_decision_tree(file: UploadFile = File(...), use_ml: bool = True):
    """
    AI Business Rules & Decision Tree Engine endpoint
    - Uses ML algorithms for pattern recognition first
    - Then applies explicit IF-ELSE business rules
    - Provides transparent, explainable decision-making
    """
    try:
        # Read file content
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Load dataframe
        df = None
        if file_extension == 'csv':
            try:
                df = parse_csv_robust(contents)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}. Please check your CSV file format.")
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(BytesIO(contents))
        else:
            try:
                df = parse_csv_robust(contents)
            except:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. Supported formats: CSV, XLS, XLSX")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Analyze using Decision Tree Engine
        result = analyze_hr_with_decision_tree(df, use_ml=use_ml)
        
        # Format output according to requirements
        formatted_result = {
            "detected_purpose": result.get("detected_purpose", "Unknown"),
            "purpose_confidence": result.get("purpose_confidence", "Low"),
            "matched_keywords": result.get("matched_keywords", []),
            "ml_pattern_recognition": result.get("ml_pattern_recognition", {}),
            "applied_rules": result.get("applied_rules", {}),
            "final_decisions_summary": result.get("final_decisions_summary", {}),
            "confidence_level": result.get("confidence_level", "Low"),
            "column_mapping": result.get("column_mapping", {}),
            "business_rules_applied": result.get("business_rules_applied", []),
            "step_by_step_reasoning": _format_step_by_step_reasoning(result)
        }
        
        return formatted_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

def _format_step_by_step_reasoning(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format step-by-step reasoning for output"""
    reasoning = []
    
    # Add purpose detection step
    reasoning.append({
        "step": 1,
        "description": f"Purpose Detection: Detected as '{result.get('detected_purpose', 'Unknown')}' with {result.get('purpose_confidence', 'Low')} confidence",
        "keywords_matched": result.get("matched_keywords", [])
    })
    
    # Add ML pattern recognition step
    ml_patterns = result.get("ml_pattern_recognition", {})
    if ml_patterns and "error" not in ml_patterns:
        reasoning.append({
            "step": 2,
            "description": "ML Pattern Recognition: Applied machine learning algorithms to discover patterns",
            "ml_rules_count": len(ml_patterns.get("ml_discovered_rules", [])),
            "feature_importance": ml_patterns.get("feature_importance", {})
        })
    
    # Add business rules application step
    applied_rules = result.get("applied_rules", {})
    if applied_rules:
        reasoning.append({
            "step": 3,
            "description": f"Business Rules Application: Applied {applied_rules.get('total_rules_applied', 0)} rules across {applied_rules.get('total_records_analyzed', 0)} records",
            "average_rules_per_record": applied_rules.get("average_rules_per_record", 0)
        })
    
    # Add final decisions step
    final_decisions = result.get("final_decisions_summary", {})
    if final_decisions:
        reasoning.append({
            "step": 4,
            "description": "Final Decisions: Generated decisions based on applied rules",
            "decision_summary": final_decisions
        })
    
    return reasoning