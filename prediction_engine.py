"""
Comprehensive HR Prediction Engine
- Reads full data first
- Matches all HR keywords
- Applies category-specific business rules
- Generates predictions for each category
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from keyword_loader import load_hr_keywords, match_keywords_in_columns
from analyzer import detect_domain
import os


class HRPredictionEngine:
    """
    Comprehensive HR Prediction Engine
    Applies business rules based on matched keywords
    """
    
    def __init__(self):
        self.hr_keywords = load_hr_keywords()
        self.all_keywords = self.hr_keywords.get('ALL', [])
        self.keyword_categories = self._categorize_keywords()
    
    def _categorize_keywords(self) -> Dict[str, List[str]]:
        """Categorize HR keywords by domain"""
        return {
            "salary": ["salary", "gross_salary", "net_salary", "basic_salary", "ctc", "payroll", "hra", "allowance", "bonus", "incentive"],
            "attendance": ["attendance", "attendance_percentage", "present_days", "absent_days", "check_in", "check_out", "punch_in", "punch_out", "late_days", "early_exit", "working_days"],
            "leave": ["leave", "leave_type", "leave_days", "sick_leave", "casual_leave", "earned_leave", "lop", "leave_balance", "leave_applied"],
            "performance": ["rating", "performance", "performance_score", "performance_rating", "appraisal", "kpi", "productivity", "efficiency"],
            "employee": ["employee_id", "employee_name", "first_name", "last_name", "emp_id", "name"],
            "status": ["status", "employee_status", "attrition", "risk", "risk_level"]
        }
    
    def match_all_keywords(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Match all HR keywords in the dataset"""
        columns = df.columns.tolist()
        matched = match_keywords_in_columns(columns, self.all_keywords)
        
        # Categorize matched keywords
        categorized_matches = {}
        for category, keywords in self.keyword_categories.items():
            category_matches = [kw for kw in matched if kw in keywords]
            if category_matches:
                categorized_matches[category] = {
                    "keywords": category_matches,
                    "columns": [col for col in columns if any(kw in col.lower() for kw in category_matches)]
                }
        
        return {
            "all_matched": matched,
            "categorized": categorized_matches,
            "total_matches": len(matched)
        }
    
    def predict_salary_level(self, df: pd.DataFrame, salary_col: str) -> Dict[str, Any]:
        """Predict salary levels (High/Medium/Low) for all records"""
        if salary_col not in df.columns:
            return {"error": "Salary column not found"}
        
        # Convert to numeric
        salaries = pd.to_numeric(df[salary_col], errors='coerce')
        
        # Apply business rules
        predictions = []
        for idx, row in df.iterrows():
            salary = salaries.iloc[idx]
            if pd.isna(salary):
                level = "Unknown"
                explanation = "Salary value is missing"
            elif salary >= 80000:
                level = "High"
                explanation = f"Salary {salary:,.0f} >= 80,000, so Salary Level is High"
            elif salary >= 40000:
                level = "Medium"
                explanation = f"Salary {salary:,.0f} >= 40,000 but < 80,000, so Salary Level is Medium"
            else:
                level = "Low"
                explanation = f"Salary {salary:,.0f} < 40,000, so Salary Level is Low"
            
            # Get employee name if available
            employee_name = self._get_employee_name(row, df.columns.tolist())
            
            predictions.append({
                "record_index": int(idx),
                "employee_name": employee_name,
                "salary": float(salary) if not pd.isna(salary) else None,
                "prediction": level,
                "explanation": explanation,
                "full_record": row.to_dict()
            })
        
        # Statistics
        valid_salaries = salaries.dropna()
        stats = {
            "highest": float(valid_salaries.max()) if len(valid_salaries) > 0 else None,
            "lowest": float(valid_salaries.min()) if len(valid_salaries) > 0 else None,
            "average": float(valid_salaries.mean()) if len(valid_salaries) > 0 else None,
            "median": float(valid_salaries.median()) if len(valid_salaries) > 0 else None,
            "high_count": sum(1 for p in predictions if p["prediction"] == "High"),
            "medium_count": sum(1 for p in predictions if p["prediction"] == "Medium"),
            "low_count": sum(1 for p in predictions if p["prediction"] == "Low")
        }
        
        # Find highest salary record
        if stats["highest"]:
            highest_record = next((p for p in predictions if p["salary"] == stats["highest"]), None)
            stats["highest_record"] = highest_record
        
        return {
            "predictions": predictions,
            "statistics": stats,
            "business_rule": "IF salary >= 80000 → High | IF salary >= 40000 → Medium | ELSE → Low"
        }
    
    def predict_attendance_status(self, df: pd.DataFrame, attendance_cols: Dict[str, str]) -> Dict[str, Any]:
        """Predict attendance status and calculate percentages"""
        predictions = []
        
        # Find attendance percentage column
        attendance_pct_col = None
        for col in df.columns:
            if "attendance" in col.lower() and "percent" in col.lower():
                attendance_pct_col = col
                break
        
        # Find present/absent days
        present_col = None
        absent_col = None
        for col in df.columns:
            if "present" in col.lower() and "day" in col.lower():
                present_col = col
            if "absent" in col.lower() and "day" in col.lower():
                absent_col = col
        
        # Calculate attendance percentage if not available
        if attendance_pct_col and attendance_pct_col in df.columns:
            attendance_pcts = pd.to_numeric(df[attendance_pct_col], errors='coerce')
        elif present_col and absent_col:
            present_days = pd.to_numeric(df[present_col], errors='coerce')
            absent_days = pd.to_numeric(df[absent_col], errors='coerce')
            total_days = present_days + absent_days
            attendance_pcts = (present_days / total_days * 100).replace([np.inf, -np.inf], np.nan)
        else:
            attendance_pcts = pd.Series([None] * len(df))
        
        # Analyze each record
        for idx, row in df.iterrows():
            attendance_pct = attendance_pcts.iloc[idx] if idx < len(attendance_pcts) else None
            
            if pd.isna(attendance_pct):
                status = "Unknown"
                category = "Unknown"
                explanation = "Attendance percentage not available"
            elif attendance_pct >= 90:
                status = "Excellent"
                category = "Normal"
                explanation = f"Attendance {attendance_pct:.1f}% >= 90%, so Status is Excellent (Normal)"
            elif attendance_pct >= 75:
                status = "Good"
                category = "Normal"
                explanation = f"Attendance {attendance_pct:.1f}% >= 75% but < 90%, so Status is Good (Normal)"
            elif attendance_pct >= 60:
                status = "Fair"
                category = "Warning"
                explanation = f"Attendance {attendance_pct:.1f}% >= 60% but < 75%, so Status is Fair (Warning)"
            else:
                status = "Poor"
                category = "Worst"
                explanation = f"Attendance {attendance_pct:.1f}% < 60%, so Status is Poor (Worst)"
            
            employee_name = self._get_employee_name(row, df.columns.tolist())
            
            predictions.append({
                "record_index": int(idx),
                "employee_name": employee_name,
                "attendance_percentage": float(attendance_pct) if not pd.isna(attendance_pct) else None,
                "status": status,
                "category": category,
                "explanation": explanation,
                "full_record": row.to_dict()
            })
        
        # Statistics
        valid_pcts = attendance_pcts.dropna()
        stats = {
            "average_percentage": float(valid_pcts.mean()) if len(valid_pcts) > 0 else None,
            "normal_count": sum(1 for p in predictions if p["category"] == "Normal"),
            "warning_count": sum(1 for p in predictions if p["category"] == "Warning"),
            "worst_count": sum(1 for p in predictions if p["category"] == "Worst"),
            "excellent_count": sum(1 for p in predictions if p["status"] == "Excellent"),
            "good_count": sum(1 for p in predictions if p["status"] == "Good"),
            "fair_count": sum(1 for p in predictions if p["status"] == "Fair"),
            "poor_count": sum(1 for p in predictions if p["status"] == "Poor")
        }
        
        # Find best and worst
        if len(valid_pcts) > 0:
            best_pct = valid_pcts.max()
            worst_pct = valid_pcts.min()
            stats["best_percentage"] = float(best_pct)
            stats["worst_percentage"] = float(worst_pct)
            stats["best_record"] = next((p for p in predictions if p["attendance_percentage"] == best_pct), None)
            stats["worst_record"] = next((p for p in predictions if p["attendance_percentage"] == worst_pct), None)
        
        return {
            "predictions": predictions,
            "statistics": stats,
            "business_rule": "IF attendance >= 90% → Excellent (Normal) | IF >= 75% → Good (Normal) | IF >= 60% → Fair (Warning) | ELSE → Poor (Worst)"
        }
    
    def predict_leave_analysis(self, df: pd.DataFrame, leave_cols: Dict[str, str]) -> Dict[str, Any]:
        """Analyze leave data with person names"""
        predictions = []
        
        leave_type_col = leave_cols.get("leave_type")
        leave_days_col = leave_cols.get("leave_days")
        
        for idx, row in df.iterrows():
            employee_name = self._get_employee_name(row, df.columns.tolist())
            
            leave_type = str(row[leave_type_col]).strip() if leave_type_col and leave_type_col in df.columns and pd.notna(row[leave_type_col]) else None
            leave_days = None
            if leave_days_col and leave_days_col in df.columns:
                leave_days = pd.to_numeric(row[leave_days_col], errors='coerce')
                if pd.isna(leave_days):
                    leave_days = None
                else:
                    leave_days = float(leave_days)
            
            # Apply leave decision logic
            if leave_type:
                if leave_type.lower() == "casual":
                    if leave_days is not None and leave_days <= 2:
                        status = "Approved"
                        explanation = f"Leave type is Casual and days ({leave_days}) <= 2, so Status is Approved"
                    else:
                        status = "Rejected"
                        explanation = f"Leave type is Casual but days ({leave_days if leave_days else 'N/A'}) > 2, so Status is Rejected"
                elif leave_type.lower() == "sick":
                    status = "Approved (with proof)"
                    explanation = f"Leave type is Sick, requires medical proof for approval"
                elif leave_type.upper() == "LOP":
                    status = "LOP - Salary Deduction"
                    explanation = f"Leave type is LOP (Loss of Pay), salary will be deducted"
                else:
                    status = "Pending Review"
                    explanation = f"Leave type is {leave_type}, requires review"
            else:
                status = "Unknown"
                explanation = "Leave type not specified"
            
            predictions.append({
                "record_index": int(idx),
                "employee_name": employee_name,
                "leave_type": leave_type,
                "leave_days": leave_days,
                "status": status,
                "explanation": explanation,
                "full_record": row.to_dict()
            })
        
        # Statistics
        stats = {
            "total_records": len(predictions),
            "approved_count": sum(1 for p in predictions if "Approved" in p["status"]),
            "rejected_count": sum(1 for p in predictions if "Rejected" in p["status"]),
            "lop_count": sum(1 for p in predictions if "LOP" in p["status"]),
            "by_leave_type": {}
        }
        
        # Group by leave type
        for pred in predictions:
            lt = pred["leave_type"] or "Unknown"
            if lt not in stats["by_leave_type"]:
                stats["by_leave_type"][lt] = 0
            stats["by_leave_type"][lt] += 1
        
        return {
            "predictions": predictions,
            "statistics": stats,
            "business_rule": "IF leave_type = Casual AND days <= 2 → Approved | IF leave_type = Sick → Approved (with proof) | IF leave_type = LOP → Salary Deduction"
        }
    
    def predict_performance_level(self, df: pd.DataFrame, performance_col: str) -> Dict[str, Any]:
        """Predict performance levels"""
        if performance_col not in df.columns:
            return {"error": "Performance column not found"}
        
        ratings = pd.to_numeric(df[performance_col], errors='coerce')
        
        predictions = []
        for idx, row in df.iterrows():
            rating = ratings.iloc[idx]
            employee_name = self._get_employee_name(row, df.columns.tolist())
            
            if pd.isna(rating):
                level = "Unknown"
                explanation = "Rating value is missing"
            elif rating >= 4.5:
                level = "Excellent"
                increment = 20
                explanation = f"Rating {rating} >= 4.5, so Performance is Excellent, Increment = 20%"
            elif rating >= 3.0:
                level = "Good"
                increment = 10
                explanation = f"Rating {rating} >= 3.0 but < 4.5, so Performance is Good, Increment = 10%"
            else:
                level = "Needs Improvement"
                increment = 0
                explanation = f"Rating {rating} < 3.0, so Performance is Needs Improvement, Increment = 0%"
            
            predictions.append({
                "record_index": int(idx),
                "employee_name": employee_name,
                "rating": float(rating) if not pd.isna(rating) else None,
                "performance_level": level,
                "increment_percentage": increment,
                "explanation": explanation,
                "full_record": row.to_dict()
            })
        
        # Statistics
        valid_ratings = ratings.dropna()
        stats = {
            "highest_rating": float(valid_ratings.max()) if len(valid_ratings) > 0 else None,
            "lowest_rating": float(valid_ratings.min()) if len(valid_ratings) > 0 else None,
            "average_rating": float(valid_ratings.mean()) if len(valid_ratings) > 0 else None,
            "excellent_count": sum(1 for p in predictions if p["performance_level"] == "Excellent"),
            "good_count": sum(1 for p in predictions if p["performance_level"] == "Good"),
            "needs_improvement_count": sum(1 for p in predictions if p["performance_level"] == "Needs Improvement")
        }
        
        if stats["highest_rating"]:
            stats["highest_record"] = next((p for p in predictions if p["rating"] == stats["highest_rating"]), None)
        
        return {
            "predictions": predictions,
            "statistics": stats,
            "business_rule": "IF rating >= 4.5 → Excellent (20% increment) | IF rating >= 3.0 → Good (10% increment) | ELSE → Needs Improvement (0% increment)"
        }
    
    def _get_employee_name(self, row: pd.Series, columns: List[str]) -> str:
        """Extract employee name from row"""
        name_keywords = ["name", "employee_name", "first_name", "last_name", "emp_name"]
        for col in columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in name_keywords):
                name = row[col]
                if pd.notna(name):
                    return str(name)
        
        # Try to combine first_name and last_name
        first_name_col = next((col for col in columns if "first_name" in col.lower()), None)
        last_name_col = next((col for col in columns if "last_name" in col.lower()), None)
        
        if first_name_col and last_name_col:
            first = row[first_name_col] if pd.notna(row[first_name_col]) else ""
            last = row[last_name_col] if pd.notna(row[last_name_col]) else ""
            if first or last:
                return f"{first} {last}".strip()
        
        return "Unknown"
    
    def comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive analysis - reads full data and applies all predictions
        """
        # Step 1: Match all keywords
        keyword_matches = self.match_all_keywords(df)
        
        # Step 2: Detect domain
        domain_info = detect_domain(df)
        
        # Step 3: Apply predictions for each category
        predictions = {}
        
        # Salary predictions
        if "salary" in keyword_matches["categorized"]:
            salary_cols = keyword_matches["categorized"]["salary"]["columns"]
            if salary_cols:
                salary_col = salary_cols[0]  # Use first matched column
                predictions["salary"] = self.predict_salary_level(df, salary_col)
        
        # Attendance predictions
        if "attendance" in keyword_matches["categorized"]:
            attendance_cols = keyword_matches["categorized"]["attendance"]["columns"]
            attendance_mapping = {}
            for col in attendance_cols:
                col_lower = col.lower()
                if "punch_in" in col_lower or "check_in" in col_lower:
                    attendance_mapping["punch_in"] = col
                elif "punch_out" in col_lower or "check_out" in col_lower:
                    attendance_mapping["punch_out"] = col
                elif "attendance" in col_lower and "percent" in col_lower:
                    attendance_mapping["attendance_percentage"] = col
                elif "present" in col_lower:
                    attendance_mapping["present_days"] = col
                elif "absent" in col_lower:
                    attendance_mapping["absent_days"] = col
            
            if attendance_mapping:
                predictions["attendance"] = self.predict_attendance_status(df, attendance_mapping)
        
        # Leave predictions
        if "leave" in keyword_matches["categorized"]:
            leave_cols = keyword_matches["categorized"]["leave"]["columns"]
            leave_mapping = {}
            for col in leave_cols:
                col_lower = col.lower()
                if "leave_type" in col_lower or "type" in col_lower:
                    leave_mapping["leave_type"] = col
                elif "leave_days" in col_lower or "days" in col_lower:
                    leave_mapping["leave_days"] = col
            
            if leave_mapping:
                predictions["leave"] = self.predict_leave_analysis(df, leave_mapping)
        
        # Performance predictions
        if "performance" in keyword_matches["categorized"]:
            perf_cols = keyword_matches["categorized"]["performance"]["columns"]
            if perf_cols:
                perf_col = perf_cols[0]
                predictions["performance"] = self.predict_performance_level(df, perf_col)
        
        return {
            "domain": domain_info.get("domain", "Unknown"),
            "domain_confidence": domain_info.get("confidence", "Low"),
            "keyword_matches": keyword_matches,
            "predictions": predictions,
            "total_records": len(df),
            "total_columns": len(df.columns)
        }


def analyze_with_prediction_engine(df: pd.DataFrame) -> Dict[str, Any]:
    """Main entry point for comprehensive prediction analysis"""
    engine = HRPredictionEngine()
    return engine.comprehensive_analysis(df)

