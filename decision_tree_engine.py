"""
AI Business Rules & Decision Tree Engine for HR Domain
- Uses ML algorithms for pattern recognition first
- Then applies explicit IF-ELSE business rules
- Provides transparent, explainable decision-making
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from keyword_loader import load_hr_keywords, match_keywords_in_columns
from ml_analyzer import MLBusinessRulesEngine, discover_apriori_patterns
from analyzer import detect_domain, profile_dataset
import os


class HRDecisionTreeEngine:
    """
    Main Decision Tree Engine for HR Domain
    Combines ML pattern recognition with explicit business rules
    """
    
    def __init__(self):
        self.ml_engine = MLBusinessRulesEngine()
        self.purpose_keywords = self._load_purpose_keywords()
        self.business_rules = self._load_business_rules()
    
    def _load_purpose_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for purpose detection"""
        return {
            "Employee Analysis": ["employee_id", "employee", "staff", "emp_id", "emp"],
            "Salary Analysis": ["salary", "payroll", "ctc", "gross_salary", "net_salary", "basic_salary"],
            "Attendance Analysis": ["punch_in", "punch_out", "attendance", "check_in", "check_out", "punch"],
            "Leave Analysis": ["leave", "leave_type", "lop", "sick_leave", "casual_leave", "leave_days"],
            "Performance Analysis": ["rating", "performance", "appraisal", "performance_score", "performance_rating", "kpi"]
        }
    
    def _load_business_rules(self) -> Dict[str, Any]:
        """Load explicit business rules"""
        return {
            "salary_level": {
                "rule": "IF salary >= 80000 → Salary_Level = High\nELSE IF salary >= 40000 → Salary_Level = Medium\nELSE → Salary_Level = Low",
                "thresholds": {"high": 80000, "medium": 40000}
            },
            "attendance_time_check": {
                "rule": "IF punch_in <= office_start_time → Status = On Time\nELSE → Status = Late",
                "default_office_start": "09:00"
            },
            "attendance_exit_check": {
                "rule": "IF punch_out >= office_end_time → Exit = Full Day\nELSE → Exit = Early Exit",
                "default_office_end": "18:00"
            },
            "working_hours": {
                "rule": "IF working_hours >= 8 → Day_Status = Full Day\nELSE IF working_hours >= 4 → Day_Status = Half Day\nELSE → Day_Status = Absent",
                "thresholds": {"full_day": 8, "half_day": 4}
            },
            "leave_decision": {
                "rule": "IF leave_type = Casual AND leave_days <= 2 → Leave_Status = Approved\nELSE IF leave_type = Sick AND medical_proof = Yes → Leave_Status = Approved\nELSE → Leave_Status = Rejected",
                "casual_max_days": 2
            },
            "leave_salary_deduction": {
                "rule": "IF leave_type = LOP → Salary_Deduction = Yes"
            },
            "performance_rating": {
                "rule": "IF rating >= 4.5 → Performance = Excellent\nELSE IF rating >= 3 → Performance = Good\nELSE → Performance = Needs Improvement",
                "thresholds": {"excellent": 4.5, "good": 3.0}
            },
            "increment_decision": {
                "rule": "IF Performance = Excellent → Increment = 20%\nELSE IF Performance = Good → Increment = 10%\nELSE → Increment = 0%",
                "increments": {"excellent": 20, "good": 10, "needs_improvement": 0}
            },
            "final_employee_status": {
                "rule": "IF attendance_good AND performance_good AND no_disciplinary_issues → Employee_Status = Active\nELSE → Employee_Status = Review Required"
            }
        }
    
    def detect_purpose(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect the purpose of the dataset using keywords
        Returns: purpose, confidence, matched_keywords
        """
        columns_lower = [col.lower() for col in df.columns]
        col_text = " ".join(columns_lower)
        
        purpose_scores = {}
        matched_keywords_all = {}
        
        for purpose, keywords in self.purpose_keywords.items():
            score = 0
            matched = []
            for keyword in keywords:
                for col in columns_lower:
                    if keyword in col or col in keyword:
                        score += 1
                        if keyword not in matched:
                            matched.append(keyword)
            purpose_scores[purpose] = score
            matched_keywords_all[purpose] = matched
        
        # Determine primary purpose
        if max(purpose_scores.values()) > 0:
            detected_purpose = max(purpose_scores, key=purpose_scores.get)
            confidence = "High" if purpose_scores[detected_purpose] >= 3 else "Medium" if purpose_scores[detected_purpose] >= 1 else "Low"
        else:
            detected_purpose = "General HR Analysis"
            confidence = "Low"
            matched_keywords_all[detected_purpose] = []
        
        return {
            "purpose": detected_purpose,
            "confidence": confidence,
            "matched_keywords": matched_keywords_all.get(detected_purpose, []),
            "all_scores": purpose_scores
        }
    
    def find_column_mapping(self, df: pd.DataFrame, purpose: str) -> Dict[str, Optional[str]]:
        """
        Find relevant columns in the dataset for applying business rules
        Returns mapping of rule fields to actual column names
        """
        columns_lower = {col.lower(): col for col in df.columns}
        mapping = {}
        
        # Salary-related columns
        for keyword in ["salary", "gross_salary", "net_salary", "basic_salary", "ctc", "payroll"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col and "id" not in lower_col:
                    mapping["salary"] = orig_col
                    break
            if "salary" in mapping:
                break
        
        # Attendance-related columns
        for keyword in ["punch_in", "check_in", "punchin", "checkin"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["punch_in"] = orig_col
                    break
            if "punch_in" in mapping:
                break
        
        for keyword in ["punch_out", "check_out", "punchout", "checkout"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["punch_out"] = orig_col
                    break
            if "punch_out" in mapping:
                break
        
        # Working hours
        for keyword in ["working_hours", "working_hours", "hours", "total_hours"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col and "overtime" not in lower_col:
                    mapping["working_hours"] = orig_col
                    break
            if "working_hours" in mapping:
                break
        
        # Leave-related
        for keyword in ["leave_type", "leave_type", "type_of_leave"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["leave_type"] = orig_col
                    break
            if "leave_type" in mapping:
                break
        
        for keyword in ["leave_days", "days", "number_of_days"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col and "leave" in lower_col:
                    mapping["leave_days"] = orig_col
                    break
            if "leave_days" in mapping:
                break
        
        for keyword in ["medical_proof", "proof", "medical_certificate"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["medical_proof"] = orig_col
                    break
            if "medical_proof" in mapping:
                break
        
        # Performance-related
        for keyword in ["rating", "performance_rating", "performance_score", "appraisal_rating"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["rating"] = orig_col
                    break
            if "rating" in mapping:
                break
        
        # Office times (may not exist, use defaults)
        for keyword in ["office_start_time", "start_time", "office_start"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["office_start_time"] = orig_col
                    break
        
        for keyword in ["office_end_time", "end_time", "office_end"]:
            for lower_col, orig_col in columns_lower.items():
                if keyword in lower_col:
                    mapping["office_end_time"] = orig_col
                    break
        
        return mapping
    
    def apply_salary_level_rule(self, row: pd.Series, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply salary level decision rule"""
        if "salary" not in mapping or mapping["salary"] is None:
            return {"applied": False, "reason": "Salary column not found"}
        
        salary_col = mapping["salary"]
        if pd.isna(row[salary_col]):
            return {"applied": False, "reason": "Salary value is missing"}
        
        salary = float(row[salary_col])
        thresholds = self.business_rules["salary_level"]["thresholds"]
        
        if salary >= thresholds["high"]:
            level = "High"
            explanation = f"Salary {salary} is >= {thresholds['high']}, so Salary Level is High"
        elif salary >= thresholds["medium"]:
            level = "Medium"
            explanation = f"Salary {salary} is >= {thresholds['medium']} but < {thresholds['high']}, so Salary Level is Medium"
        else:
            level = "Low"
            explanation = f"Salary {salary} is < {thresholds['medium']}, so Salary Level is Low"
        
        return {
            "applied": True,
            "rule": "EMPLOYEE → SALARY LEVEL",
            "decision": f"Salary_Level = {level}",
            "explanation": explanation,
            "confidence": "High"
        }
    
    def apply_attendance_time_check(self, row: pd.Series, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply attendance time check rule"""
        if "punch_in" not in mapping or mapping["punch_in"] is None:
            return {"applied": False, "reason": "Punch-in column not found"}
        
        punch_in_col = mapping["punch_in"]
        if pd.isna(row[punch_in_col]):
            return {"applied": False, "reason": "Punch-in time is missing"}
        
        office_start = mapping.get("office_start_time")
        if office_start and not pd.isna(row[office_start]):
            office_start_time = str(row[office_start])
        else:
            office_start_time = self.business_rules["attendance_time_check"]["default_office_start"]
        
        punch_in_time = str(row[punch_in_col])
        
        # Simple time comparison (assuming HH:MM format)
        try:
            punch_hour, punch_min = map(int, punch_in_time.split(":")[:2])
            office_hour, office_min = map(int, office_start_time.split(":")[:2])
            
            punch_minutes = punch_hour * 60 + punch_min
            office_minutes = office_hour * 60 + office_min
            
            if punch_minutes <= office_minutes:
                status = "On Time"
                explanation = f"Punch-in time {punch_in_time} is <= office start time {office_start_time}, so Status is On Time"
            else:
                status = "Late"
                explanation = f"Punch-in time {punch_in_time} is > office start time {office_start_time}, so Status is Late"
            
            return {
                "applied": True,
                "rule": "ATTENDANCE → TIME CHECK",
                "decision": f"Status = {status}",
                "explanation": explanation,
                "confidence": "High"
            }
        except:
            return {"applied": False, "reason": "Could not parse time values"}
    
    def apply_attendance_exit_check(self, row: pd.Series, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply attendance exit check rule"""
        if "punch_out" not in mapping or mapping["punch_out"] is None:
            return {"applied": False, "reason": "Punch-out column not found"}
        
        punch_out_col = mapping["punch_out"]
        if pd.isna(row[punch_out_col]):
            return {"applied": False, "reason": "Punch-out time is missing"}
        
        office_end = mapping.get("office_end_time")
        if office_end and not pd.isna(row[office_end]):
            office_end_time = str(row[office_end])
        else:
            office_end_time = self.business_rules["attendance_exit_check"]["default_office_end"]
        
        punch_out_time = str(row[punch_out_col])
        
        try:
            punch_hour, punch_min = map(int, punch_out_time.split(":")[:2])
            office_hour, office_min = map(int, office_end_time.split(":")[:2])
            
            punch_minutes = punch_hour * 60 + punch_min
            office_minutes = office_hour * 60 + office_min
            
            if punch_minutes >= office_minutes:
                exit_status = "Full Day"
                explanation = f"Punch-out time {punch_out_time} is >= office end time {office_end_time}, so Exit is Full Day"
            else:
                exit_status = "Early Exit"
                explanation = f"Punch-out time {punch_out_time} is < office end time {office_end_time}, so Exit is Early Exit"
            
            return {
                "applied": True,
                "rule": "ATTENDANCE → EXIT CHECK",
                "decision": f"Exit = {exit_status}",
                "explanation": explanation,
                "confidence": "High"
            }
        except:
            return {"applied": False, "reason": "Could not parse time values"}
    
    def apply_working_hours_rule(self, row: pd.Series, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply working hours decision rule"""
        if "working_hours" not in mapping or mapping["working_hours"] is None:
            return {"applied": False, "reason": "Working hours column not found"}
        
        hours_col = mapping["working_hours"]
        if pd.isna(row[hours_col]):
            return {"applied": False, "reason": "Working hours value is missing"}
        
        hours = float(row[hours_col])
        thresholds = self.business_rules["working_hours"]["thresholds"]
        
        if hours >= thresholds["full_day"]:
            day_status = "Full Day"
            explanation = f"Working hours {hours} is >= {thresholds['full_day']}, so Day Status is Full Day"
        elif hours >= thresholds["half_day"]:
            day_status = "Half Day"
            explanation = f"Working hours {hours} is >= {thresholds['half_day']} but < {thresholds['full_day']}, so Day Status is Half Day"
        else:
            day_status = "Absent"
            explanation = f"Working hours {hours} is < {thresholds['half_day']}, so Day Status is Absent"
        
        return {
            "applied": True,
            "rule": "WORKING HOURS",
            "decision": f"Day_Status = {day_status}",
            "explanation": explanation,
            "confidence": "High"
        }
    
    def apply_leave_decision_rule(self, row: pd.Series, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply leave decision rule"""
        if "leave_type" not in mapping or mapping["leave_type"] is None:
            return {"applied": False, "reason": "Leave type column not found"}
        
        leave_type_col = mapping["leave_type"]
        if pd.isna(row[leave_type_col]):
            return {"applied": False, "reason": "Leave type is missing"}
        
        leave_type = str(row[leave_type_col]).strip()
        leave_days = None
        medical_proof = None
        
        if "leave_days" in mapping and mapping["leave_days"]:
            if not pd.isna(row[mapping["leave_days"]]):
                leave_days = float(row[mapping["leave_days"]])
        
        if "medical_proof" in mapping and mapping["medical_proof"]:
            if not pd.isna(row[mapping["medical_proof"]]):
                medical_proof = str(row[mapping["medical_proof"]]).strip().lower()
        
        # Apply leave decision logic
        if leave_type.lower() == "casual":
            if leave_days is not None and leave_days <= self.business_rules["leave_decision"]["casual_max_days"]:
                status = "Approved"
                explanation = f"Leave type is Casual and leave days ({leave_days}) <= {self.business_rules['leave_decision']['casual_max_days']}, so Leave Status is Approved"
            else:
                status = "Rejected"
                explanation = f"Leave type is Casual but leave days ({leave_days if leave_days else 'N/A'}) > {self.business_rules['leave_decision']['casual_max_days']}, so Leave Status is Rejected"
        elif leave_type.lower() == "sick":
            if medical_proof and medical_proof in ["yes", "y", "true", "1"]:
                status = "Approved"
                explanation = f"Leave type is Sick and medical proof is Yes, so Leave Status is Approved"
            else:
                status = "Rejected"
                explanation = f"Leave type is Sick but medical proof is not Yes, so Leave Status is Rejected"
        else:
            status = "Rejected"
            explanation = f"Leave type is {leave_type}, which doesn't match Casual or Sick criteria, so Leave Status is Rejected"
        
        # Check for LOP salary deduction
        salary_deduction = "No"
        if leave_type.upper() == "LOP":
            salary_deduction = "Yes"
            explanation += f". Since leave type is LOP, Salary Deduction = Yes"
        
        return {
            "applied": True,
            "rule": "LEAVE DECISION",
            "decision": f"Leave_Status = {status}, Salary_Deduction = {salary_deduction}",
            "explanation": explanation,
            "confidence": "High"
        }
    
    def apply_performance_rating_rule(self, row: pd.Series, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Apply performance rating rule"""
        if "rating" not in mapping or mapping["rating"] is None:
            return {"applied": False, "reason": "Rating column not found"}
        
        rating_col = mapping["rating"]
        if pd.isna(row[rating_col]):
            return {"applied": False, "reason": "Rating value is missing"}
        
        rating = float(row[rating_col])
        thresholds = self.business_rules["performance_rating"]["thresholds"]
        
        if rating >= thresholds["excellent"]:
            performance = "Excellent"
            explanation = f"Rating {rating} is >= {thresholds['excellent']}, so Performance is Excellent"
        elif rating >= thresholds["good"]:
            performance = "Good"
            explanation = f"Rating {rating} is >= {thresholds['good']} but < {thresholds['excellent']}, so Performance is Good"
        else:
            performance = "Needs Improvement"
            explanation = f"Rating {rating} is < {thresholds['good']}, so Performance is Needs Improvement"
        
        return {
            "applied": True,
            "rule": "PERFORMANCE RATING",
            "decision": f"Performance = {performance}",
            "explanation": explanation,
            "confidence": "High"
        }
    
    def apply_increment_decision_rule(self, performance: str) -> Dict[str, Any]:
        """Apply increment decision based on performance"""
        increments = self.business_rules["increment_decision"]["increments"]
        
        if performance == "Excellent":
            increment = increments["excellent"]
        elif performance == "Good":
            increment = increments["good"]
        else:
            increment = increments["needs_improvement"]
        
        return {
            "applied": True,
            "rule": "INCREMENT DECISION",
            "decision": f"Increment = {increment}%",
            "explanation": f"Since Performance is {performance}, Increment is {increment}%",
            "confidence": "High"
        }
    
    def apply_final_employee_status(self, row: pd.Series, mapping: Dict[str, Optional[str]], 
                                     applied_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply final employee status rule"""
        # Extract information from applied rules
        attendance_good = True
        performance_good = False
        no_disciplinary_issues = True  # Assume true unless we find evidence
        
        # Check attendance from applied rules
        for rule_result in applied_rules:
            if "rule" in rule_result:
                if "TIME CHECK" in rule_result["rule"]:
                    if "Late" in rule_result.get("decision", ""):
                        attendance_good = False
                if "EXIT CHECK" in rule_result["rule"]:
                    if "Early Exit" in rule_result.get("decision", ""):
                        attendance_good = False
                if "WORKING HOURS" in rule_result["rule"]:
                    if "Absent" in rule_result.get("decision", ""):
                        attendance_good = False
        
        # Check performance
        for rule_result in applied_rules:
            if "PERFORMANCE RATING" in rule_result.get("rule", ""):
                if "Excellent" in rule_result.get("decision", "") or "Good" in rule_result.get("decision", ""):
                    performance_good = True
        
        # Final decision
        if attendance_good and performance_good and no_disciplinary_issues:
            status = "Active"
            explanation = "Employee has good attendance, good performance, and no disciplinary issues, so Employee Status is Active"
        else:
            status = "Review Required"
            reasons = []
            if not attendance_good:
                reasons.append("attendance issues")
            if not performance_good:
                reasons.append("performance issues")
            explanation = f"Employee has {', '.join(reasons) if reasons else 'issues'}, so Employee Status is Review Required"
        
        return {
            "applied": True,
            "rule": "FINAL EMPLOYEE STATUS",
            "decision": f"Employee_Status = {status}",
            "explanation": explanation,
            "confidence": "Medium"
        }
    
    def analyze_record(self, row: pd.Series, mapping: Dict[str, Optional[str]], 
                       purpose: str) -> Dict[str, Any]:
        """
        Analyze a single record and apply all applicable business rules
        Returns step-by-step decision tree reasoning
        """
        applied_rules = []
        decisions = {}
        
        # Apply rules based on purpose and available columns
        if "Salary" in purpose and "salary" in mapping and mapping["salary"]:
            result = self.apply_salary_level_rule(row, mapping)
            if result.get("applied"):
                applied_rules.append(result)
                decisions["Salary_Level"] = result["decision"].split("=")[1].strip()
        
        if "Attendance" in purpose:
            if "punch_in" in mapping and mapping["punch_in"]:
                result = self.apply_attendance_time_check(row, mapping)
                if result.get("applied"):
                    applied_rules.append(result)
                    decisions["Attendance_Status"] = result["decision"].split("=")[1].strip()
            
            if "punch_out" in mapping and mapping["punch_out"]:
                result = self.apply_attendance_exit_check(row, mapping)
                if result.get("applied"):
                    applied_rules.append(result)
                    decisions["Exit_Status"] = result["decision"].split("=")[1].strip()
            
            if "working_hours" in mapping and mapping["working_hours"]:
                result = self.apply_working_hours_rule(row, mapping)
                if result.get("applied"):
                    applied_rules.append(result)
                    decisions["Day_Status"] = result["decision"].split("=")[1].strip()
        
        if "Leave" in purpose and "leave_type" in mapping and mapping["leave_type"]:
            result = self.apply_leave_decision_rule(row, mapping)
            if result.get("applied"):
                applied_rules.append(result)
                if "Leave_Status" in result["decision"]:
                    decisions["Leave_Status"] = result["decision"].split("Leave_Status =")[1].split(",")[0].strip()
                if "Salary_Deduction" in result["decision"]:
                    decisions["Salary_Deduction"] = result["decision"].split("Salary_Deduction =")[1].strip()
        
        if "Performance" in purpose and "rating" in mapping and mapping["rating"]:
            result = self.apply_performance_rating_rule(row, mapping)
            if result.get("applied"):
                applied_rules.append(result)
                decisions["Performance"] = result["decision"].split("=")[1].strip()
                
                # Apply increment decision based on performance
                increment_result = self.apply_increment_decision_rule(decisions["Performance"])
                applied_rules.append(increment_result)
                decisions["Increment"] = increment_result["decision"].split("=")[1].strip()
        
        # Apply final employee status if we have enough information
        if len(applied_rules) >= 2:
            final_status_result = self.apply_final_employee_status(row, mapping, applied_rules)
            applied_rules.append(final_status_result)
            decisions["Employee_Status"] = final_status_result["decision"].split("=")[1].strip()
        
        return {
            "applied_rules": applied_rules,
            "decisions": decisions
        }
    
    def analyze_dataset(self, df: pd.DataFrame, use_ml: bool = True) -> Dict[str, Any]:
        """
        Main analysis function
        Combines ML pattern recognition with explicit business rules
        """
        # Step 1: Enhanced Domain Detection using keyword_loader
        domain_info = detect_domain(df)
        purpose_info = self.detect_purpose(df)
        
        # Combine domain and purpose detection
        combined_purpose = purpose_info["purpose"]
        if domain_info.get("domain") == "HR":
            # Use HR keywords for better matching
            hr_keywords_dict = load_hr_keywords()
            hr_keywords = hr_keywords_dict.get('ALL', [])
            matched_hr_keywords = match_keywords_in_columns(df.columns.tolist(), hr_keywords)
            if matched_hr_keywords:
                purpose_info["matched_keywords"] = matched_hr_keywords[:20]  # Top 20 matches
        
        # Step 2: ML Pattern Recognition (if enabled)
        ml_patterns = {}
        ml_rules = []
        if use_ml:
            try:
                ml_results = self.ml_engine.discover_business_rules(df, domain_info["domain"])
                ml_rules = ml_results.get("rules", [])[:10]  # Top 10 ML-discovered rules
                ml_patterns = {
                    "ml_discovered_rules": [r.get("rule", "") for r in ml_rules],
                    "feature_importance": ml_results.get("feature_importance", {}),
                    "apriori_patterns": [p["pattern"] for p in discover_apriori_patterns(df, min_support=0.1)[:5]]
                }
            except Exception as e:
                ml_patterns = {"error": str(e)}
        
        # Step 3: Find column mappings with enhanced detection
        mapping = self.find_column_mapping(df, purpose_info["purpose"])
        
        # Step 4: Find highest values and statistics
        data_insights = self._find_data_insights(df, mapping)
        
        # Step 5: Apply business rules to each record
        record_analyses = []
        all_decisions_table = []  # For table format
        
        for idx, row in df.iterrows():
            analysis = self.analyze_record(row, mapping, purpose_info["purpose"])
            record_analyses.append({
                "record_index": int(idx),
                **analysis
            })
            
            # Build table row
            table_row = {"record_index": int(idx)}
            # Add original data
            for col in df.columns:
                table_row[col] = str(row[col]) if pd.notna(row[col]) else ""
            # Add decisions
            table_row.update(analysis.get("decisions", {}))
            all_decisions_table.append(table_row)
        
        # Step 6: Calculate confidence
        total_rules_applied = sum(len(a["applied_rules"]) for a in record_analyses)
        total_records = len(record_analyses)
        avg_rules_per_record = total_rules_applied / total_records if total_records > 0 else 0
        
        if avg_rules_per_record >= 3:
            confidence = "High"
        elif avg_rules_per_record >= 1:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        # Step 7: Generate table format data
        table_data = self._generate_table_data(all_decisions_table, mapping)
        
        # Step 8: Build final output
        return {
            "detected_domain": domain_info.get("domain", "Unknown"),
            "domain_confidence": domain_info.get("confidence", "Low"),
            "detected_purpose": purpose_info["purpose"],
            "purpose_confidence": purpose_info["confidence"],
            "matched_keywords": purpose_info["matched_keywords"],
            "domain_keywords_matched": domain_info.get("matched_keywords", []),
            "ml_pattern_recognition": ml_patterns,
            "column_mapping": {k: v for k, v in mapping.items() if v is not None},
            "data_insights": data_insights,  # Highest values, statistics
            "applied_rules": {
                "total_records_analyzed": total_records,
                "total_rules_applied": total_rules_applied,
                "average_rules_per_record": round(avg_rules_per_record, 2),
                "record_analyses": record_analyses[:10]  # Show first 10 records
            },
            "table_data": table_data,  # Table format for display
            "final_decisions_summary": self._summarize_decisions(record_analyses),
            "confidence_level": confidence,
            "business_rules_applied": [r["rule"] for r in record_analyses[0]["applied_rules"] if record_analyses] if record_analyses else []
        }
    
    def _find_data_insights(self, df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Find highest values, statistics, and insights from data"""
        insights = {}
        
        # Find highest salary
        if "salary" in mapping and mapping["salary"]:
            salary_col = mapping["salary"]
            if salary_col in df.columns:
                numeric_salaries = pd.to_numeric(df[salary_col], errors='coerce').dropna()
                if len(numeric_salaries) > 0:
                    max_salary = numeric_salaries.max()
                    min_salary = numeric_salaries.min()
                    avg_salary = numeric_salaries.mean()
                    max_idx = numeric_salaries.idxmax()
                    
                    insights["salary"] = {
                        "highest": float(max_salary),
                        "lowest": float(min_salary),
                        "average": float(avg_salary),
                        "highest_record_index": int(max_idx),
                        "highest_record_data": df.loc[max_idx].to_dict() if max_idx in df.index else {}
                    }
        
        # Find attendance insights
        if "punch_in" in mapping and mapping["punch_in"]:
            punch_in_col = mapping["punch_in"]
            if punch_in_col in df.columns:
                # Find earliest and latest punch in times
                punch_times = df[punch_in_col].dropna()
                if len(punch_times) > 0:
                    insights["attendance"] = {
                        "punch_in_column": punch_in_col,
                        "total_records": len(punch_times),
                        "sample_times": punch_times.head(10).tolist()
                    }
        
        # Find working hours insights
        if "working_hours" in mapping and mapping["working_hours"]:
            hours_col = mapping["working_hours"]
            if hours_col in df.columns:
                numeric_hours = pd.to_numeric(df[hours_col], errors='coerce').dropna()
                if len(numeric_hours) > 0:
                    insights["working_hours"] = {
                        "maximum": float(numeric_hours.max()),
                        "minimum": float(numeric_hours.min()),
                        "average": float(numeric_hours.mean()),
                        "total_records": len(numeric_hours)
                    }
        
        # Find performance insights
        if "rating" in mapping and mapping["rating"]:
            rating_col = mapping["rating"]
            if rating_col in df.columns:
                numeric_ratings = pd.to_numeric(df[rating_col], errors='coerce').dropna()
                if len(numeric_ratings) > 0:
                    max_rating = numeric_ratings.max()
                    max_idx = numeric_ratings.idxmax()
                    insights["performance"] = {
                        "highest_rating": float(max_rating),
                        "highest_record_index": int(max_idx),
                        "average_rating": float(numeric_ratings.mean()),
                        "total_records": len(numeric_ratings)
                    }
        
        return insights
    
    def _generate_table_data(self, all_decisions_table: List[Dict], mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Generate table format data for display"""
        if not all_decisions_table:
            return {"columns": [], "rows": []}
        
        # Get all unique column names
        all_columns = set()
        for row in all_decisions_table:
            all_columns.update(row.keys())
        
        # Define column order: original columns first, then decisions
        original_cols = [col for col in all_columns if col != "record_index" and not col.endswith("_Level") and not col.endswith("_Status") and not col.endswith("_Decision")]
        decision_cols = [col for col in all_columns if col.endswith("_Level") or col.endswith("_Status") or col.endswith("_Decision") or col in ["Performance", "Increment", "Employee_Status"]]
        
        columns = ["record_index"] + original_cols + decision_cols
        
        # Build rows
        rows = []
        for row_data in all_decisions_table:
            row = []
            for col in columns:
                row.append(str(row_data.get(col, "")))
            rows.append(row)
        
        return {
            "columns": columns,
            "rows": rows,
            "total_records": len(rows),
            "original_columns": original_cols,
            "decision_columns": decision_cols
        }
    
    def _summarize_decisions(self, record_analyses: List[Dict]) -> Dict[str, Any]:
        """Summarize decisions across all records"""
        summary = {}
        
        for analysis in record_analyses:
            for key, value in analysis.get("decisions", {}).items():
                if key not in summary:
                    summary[key] = {"values": [], "counts": {}}
                summary[key]["values"].append(value)
                summary[key]["counts"][value] = summary[key]["counts"].get(value, 0) + 1
        
        # Convert to final format
        final_summary = {}
        for key, data in summary.items():
            final_summary[key] = {
                "unique_values": list(data["counts"].keys()),
                "distribution": data["counts"],
                "total_count": len(data["values"])
            }
        
        return final_summary


def analyze_hr_with_decision_tree(df: pd.DataFrame, use_ml: bool = True) -> Dict[str, Any]:
    """
    Main entry point for HR Decision Tree Analysis
    """
    engine = HRDecisionTreeEngine()
    return engine.analyze_dataset(df, use_ml=use_ml)

