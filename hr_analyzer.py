"""
Enhanced HR Analyzer - Integrates ML-based rule discovery and prediction
Returns output in the specified JSON format
"""
import pandas as pd
import numpy as np
from analyzer import detect_domain, profile_dataset
from ml_analyzer import MLBusinessRulesEngine, discover_apriori_patterns
from keyword_loader import load_hr_keywords, match_keywords_in_columns
import os
from typing import Dict, List, Any
import uuid

def extract_important_features(df: pd.DataFrame, profile: dict) -> Dict[str, List[str]]:
    """
    Extract important features and categorize as numerical/categorical
    """
    numerical = []
    categorical = []
    
    for col_info in profile["columns"]:
        col_name = col_info["name"]
        col_type = col_info.get("type", "categorical")
        
        # Skip ID columns and dates
        if any(x in col_name.lower() for x in ['id', 'name', 'code', 'key', 'date', 'time']):
            continue
        
        if col_type == "numeric":
            numerical.append(col_name)
        elif col_type in ["categorical", "boolean"]:
            categorical.append(col_name)
    
    return {
        "numerical": numerical[:15],  # Top 15 numerical features
        "categorical": categorical[:15]  # Top 15 categorical features
    }

def format_business_rules(ml_rules: List[Dict]) -> List[str]:
    """
    Format ML-discovered rules into simple IF-THEN format
    """
    formatted_rules = []
    for rule in ml_rules[:10]:  # Top 10 rules
        rule_text = rule.get("rule", "")
        # Simplify rule text
        if "IF" in rule_text and "THEN" in rule_text:
            formatted_rules.append(rule_text)
        elif "description" in rule:
            formatted_rules.append(rule["description"])
    
    return formatted_rules

def analyze_hr_dataset(df: pd.DataFrame, dataset_id: str = None) -> Dict[str, Any]:
    """
    Main HR analysis function - Returns output in specified JSON format
    """
    if dataset_id is None:
        dataset_id = str(uuid.uuid4())
    
    # 1. Domain Detection
    domain_info = detect_domain(df)
    
    # 2. Dataset Profiling
    profile = profile_dataset(df)
    
    # 3. Extract Important Features
    important_features = extract_important_features(df, profile)
    
    # 4. ML-based Business Rules Discovery
    ml_engine = MLBusinessRulesEngine()
    ml_results = ml_engine.discover_business_rules(df, domain_info["domain"])
    
    # Format business rules
    business_rules = format_business_rules(ml_results.get("rules", []))
    
    # 5. Feature Importance
    feature_importance = ml_results.get("feature_importance", {})
    
    # 6. Apriori Pattern Discovery (hidden patterns)
    hidden_patterns = discover_apriori_patterns(df, min_support=0.1)
    formatted_patterns = [p["pattern"] for p in hidden_patterns[:5]]  # Top 5 patterns
    
    # Build response in requested format
    response = {
        "detected_domain": domain_info["domain"],
        "domain_confidence": domain_info["confidence"],
        "keywords_matched": domain_info.get("matched_keywords", [])[:10],
        "important_features": important_features,
        "business_rules": business_rules,
        "feature_importance": feature_importance,
        "hidden_patterns": formatted_patterns,
        "dataset_id": dataset_id,
        "model_available": ml_results.get("target_column") is not None
    }
    
    # Store model for later predictions
    if ml_results.get("target_column"):
        from data_storage import storage
        storage.store_model(dataset_id, ml_engine)
        response["target_column"] = ml_results.get("target_column")
    
    return response

def predict_hr_outcome(dataset_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict HR outcome for given input data
    Returns prediction in specified format
    """
    from data_storage import storage
    
    # Get model
    model = storage.get_model(dataset_id)
    if model is None:
        return {
            "error": "Model not found. Please analyze a dataset first.",
            "dataset_id": dataset_id
        }
    
    # Get dataset to understand structure
    df = storage.get_dataset(dataset_id)
    if df is None:
        return {
            "error": "Dataset not found.",
            "dataset_id": dataset_id
        }
    
    # Make prediction
    prediction_result = model.predict(input_data)
    
    if "error" in prediction_result:
        return prediction_result
    
    # Format response
    response = {
        "prediction_input": input_data,
        "predicted_outcome": prediction_result.get("predicted_outcome", "UNKNOWN"),
        "prediction_explanation": prediction_result.get("explanation", "Prediction completed."),
        "confidence": prediction_result.get("confidence", 0.0),
        "feature_importance": model.feature_importance if hasattr(model, 'feature_importance') else {}
    }
    
    # Store prediction
    prediction_id = storage.store_prediction(dataset_id, input_data, prediction_result)
    response["prediction_id"] = prediction_id
    
    return response

def analyze_and_predict_combined(df: pd.DataFrame, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Combined analysis and prediction in one call
    """
    dataset_id = str(uuid.uuid4())
    
    # Store dataset
    from data_storage import storage
    storage.store_dataset(dataset_id, df)
    
    # Analyze
    analysis_result = analyze_hr_dataset(df, dataset_id)
    
    # Predict if input data provided
    if input_data:
        prediction_result = predict_hr_outcome(dataset_id, input_data)
        analysis_result["prediction_input"] = prediction_result.get("prediction_input")
        analysis_result["predicted_outcome"] = prediction_result.get("predicted_outcome")
        analysis_result["prediction_explanation"] = prediction_result.get("prediction_explanation")
        analysis_result["prediction_confidence"] = prediction_result.get("confidence")
    
    return analysis_result

