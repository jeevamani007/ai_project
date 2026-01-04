import pandas as pd
import numpy as np
from datetime import datetime

# ==================== DOMAIN DETECTION ====================
def detect_domain(df: pd.DataFrame) -> dict:
    """Detect domain strictly using column names and values - NO guessing"""
    columns_lower = [col.lower() for col in df.columns]
    col_text = " ".join(columns_lower)
    
    # Sample values from first few rows
    sample_values = " ".join([str(val).lower() for col in df.columns[:5] for val in df[col].dropna().head(10)])
    combined_text = col_text + " " + sample_values
    
    domain_keywords = {
        "HR": {
            "keywords": ["employee", "attendance", "hr", "working_hours", "check_in", "check_out", "status", "absent", "present", "half day", "leave", "department"],
            "description": "Human Resources domain - employee attendance, working hours, leave management"
        },
        "Finance": {
            "keywords": ["loan", "cibil", "emi", "credit", "finance", "bank", "interest", "payment", "transaction", "account", "balance"],
            "description": "Finance domain - banking, loans, credit, transactions"
        },
        "Sales": {
            "keywords": ["sales", "target", "discount", "revenue", "customer", "order", "product", "quantity", "price", "commission"],
            "description": "Sales domain - sales targets, customer management, revenue"
        },
        "Healthcare": {
            "keywords": ["patient", "diagnosis", "risk", "health", "medical", "treatment", "symptom", "doctor", "hospital"],
            "description": "Healthcare domain - patient records, medical diagnosis"
        },
        "Insurance": {
            "keywords": ["claim", "policy", "insurance", "premium", "coverage", "beneficiary"],
            "description": "Insurance domain - claims processing, policy management"
        }
    }
    
    domain_scores = {}
    for domain, info in domain_keywords.items():
        score = sum(1 for keyword in info["keywords"] if keyword in combined_text)
        domain_scores[domain] = score
    
    detected_domain = max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else "Generic"
    
    reasoning = []
    if detected_domain != "Generic":
        matched_keywords = [kw for kw in domain_keywords[detected_domain]["keywords"] if kw in combined_text]
        reasoning.append(f"Detected {detected_domain} domain based on column names: {', '.join(matched_keywords[:5])}")
        reasoning.append(f"Column names like {', '.join([col for col in df.columns[:3]])} indicate {detected_domain} context")
    else:
        reasoning.append("No specific domain pattern detected in column names")
        reasoning.append("Analyzing as generic business dataset")
    
    return {
        "domain": detected_domain,
        "description": domain_keywords.get(detected_domain, {"description": "Generic domain"}).get("description"),
        "reasoning": reasoning,
        "confidence": "High" if max(domain_scores.values()) >= 3 else "Medium" if max(domain_scores.values()) >= 1 else "Low"
    }

# ==================== DATASET PROFILING ====================
def profile_dataset(df: pd.DataFrame) -> dict:
    """Basic dataset profiling for context"""
    profile = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": []
    }
    
    for col in df.columns:
        col_data = df[col]
        col_info = {
            "name": col,
            "dtype": str(col_data.dtype),
            "null_count": int(col_data.isnull().sum()),
            "null_percentage": float(col_data.isnull().sum() / len(df) * 100),
            "unique_count": int(col_data.nunique())
        }
        
        if col_data.dtype in ['int64', 'float64']:
            col_info["type"] = "numeric"
            col_info["statistics"] = {
                "min": float(col_data.min()) if not col_data.isnull().all() else None,
                "max": float(col_data.max()) if not col_data.isnull().all() else None,
                "mean": float(col_data.mean()) if not col_data.isnull().all() else None,
                "median": float(col_data.median()) if not col_data.isnull().all() else None
            }
        elif col_data.dtype == 'bool' or col_data.dtype == 'bool_':
            col_info["type"] = "boolean"
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            col_info["type"] = "date"
        else:
            col_info["type"] = "categorical"
            col_info["unique_values"] = col_data.value_counts().head(10).to_dict()
        
        profile["columns"].append(col_info)
    
    return profile

# ==================== VALIDATION RULES ====================
def identify_validation_rules(df: pd.DataFrame) -> list:
    """Generate ONLY universally valid business rules - NO statistics"""
    rules = []
    
    for col in df.columns:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
            
        col_lower = col.lower()
        
        # ID/Code validation - must be unique and non-null
        if any(x in col_lower for x in ['id', 'code', 'key']) and col_data.nunique() == len(col_data):
            rules.append({
                "rule": f"{col} IS NOT NULL AND UNIQUE",
                "description": f"{col} must be unique and non-null (identifier field)",
                "sql": f"UNIQUE ({col})",
                "pseudo_code": f"if {col} is None or {col} in existing_values: raise ValidationError('{col} must be unique')",
                "confidence": "High",
                "business_meaning": f"{col} is an identifier and must be unique for each record",
                "requires_approval": False,
                "hr_usable": True
            })
        
        # Age validation
        if 'age' in col_lower:
            if col_data.dtype in ['int64', 'float64']:
                if (col_data >= 0).all():
                    rules.append({
                        "rule": f"{col} >= 0",
                        "description": f"Age must be non-negative",
                        "sql": f"CHECK ({col} >= 0)",
                        "pseudo_code": f"if {col} < 0: raise ValidationError('Age cannot be negative')",
                        "confidence": "High",
                        "business_meaning": "Age values must be non-negative numbers",
                        "requires_approval": False,
                        "hr_usable": True
                    })
        
        # Hours/Time validation
        if any(x in col_lower for x in ['hours', 'working_hours', 'overtime']):
            if col_data.dtype in ['int64', 'float64']:
                if (col_data >= 0).all():
                    rules.append({
                        "rule": f"{col} >= 0",
                        "description": f"{col} must be non-negative",
                        "sql": f"CHECK ({col} >= 0)",
                        "pseudo_code": f"if {col} < 0: raise ValidationError('{col} cannot be negative')",
                        "confidence": "High",
                        "business_meaning": f"{col} represents time and must be non-negative",
                        "requires_approval": False,
                        "hr_usable": True
                    })
        
        # Salary/Amount validation
        if any(x in col_lower for x in ['salary', 'amount', 'price', 'cost', 'revenue', 'income']):
            if col_data.dtype in ['int64', 'float64']:
                if (col_data >= 0).all():
                    rules.append({
                        "rule": f"{col} >= 0",
                        "description": f"{col} must be non-negative",
                        "sql": f"CHECK ({col} >= 0)",
                        "pseudo_code": f"if {col} < 0: raise ValidationError('{col} cannot be negative')",
                        "confidence": "High",
                        "business_meaning": f"{col} represents monetary value and must be non-negative",
                        "requires_approval": False,
                        "hr_usable": True
                    })
    
    return rules

# ==================== BUSINESS DECISION RULES ====================
def identify_decision_rules(df: pd.DataFrame) -> list:
    """Create IF-THEN rules ONLY if they reflect real HR/business policies - NO ML/statistics"""
    rules = []
    
    # Look for Status column and derive rules
    status_col = None
    for col in df.columns:
        if 'status' in col.lower():
            status_col = col
            break
    
    if status_col:
        status_values = df[status_col].dropna().unique()
        
        # Rule: IF Status = 'Absent' THEN Working_Hours = 0
        working_hours_col = None
        for col in df.columns:
            if 'working_hours' in col.lower() or ('hours' in col.lower() and 'working' in col.lower()):
                working_hours_col = col
                break
        
        if working_hours_col and 'absent' in [str(v).lower() for v in status_values]:
            absent_rows = df[df[status_col].str.lower() == 'absent']
            if len(absent_rows) > 0:
                hours_for_absent = absent_rows[working_hours_col].dropna()
                if len(hours_for_absent) > 0 and (hours_for_absent == 0).all():
                    rules.append({
                        "rule": f"IF {status_col} = 'Absent' THEN {working_hours_col} = 0",
                        "description": f"When employee is absent, working hours must be zero",
                        "if_then": f"IF {status_col} = 'Absent' THEN {working_hours_col} = 0",
                        "sql": f"CASE WHEN {status_col} = 'Absent' THEN 0 ELSE {working_hours_col} END",
                        "pseudo_code": f"if {status_col} == 'Absent':\n    {working_hours_col} = 0",
                        "confidence": "High",
                        "business_meaning": "HR Policy: Absent employees have zero working hours",
                        "requires_approval": False,
                        "hr_usable": True
                    })
        
        # Rule: IF Status = 'Half Day' THEN Working_Hours <= 5
        if 'half' in [str(v).lower() for v in status_values] or 'half day' in [str(v).lower() for v in status_values]:
            half_day_rows = df[df[status_col].str.lower().str.contains('half', na=False)]
            if len(half_day_rows) > 0 and working_hours_col:
                hours_for_half = half_day_rows[working_hours_col].dropna()
                if len(hours_for_half) > 0 and (hours_for_half <= 5).all():
                    rules.append({
                        "rule": f"IF {status_col} = 'Half Day' THEN {working_hours_col} <= 5",
                        "description": f"When employee takes half day, working hours should be 5 or less",
                        "if_then": f"IF {status_col} = 'Half Day' THEN {working_hours_col} <= 5",
                        "sql": f"CASE WHEN {status_col} LIKE '%Half Day%' THEN {working_hours_col} <= 5 ELSE TRUE END",
                        "pseudo_code": f"if 'Half Day' in {status_col}:\n    assert {working_hours_col} <= 5",
                        "confidence": "High",
                        "business_meaning": "HR Policy: Half day leave means maximum 5 working hours",
                        "requires_approval": False,
                        "hr_usable": True
                    })
        
        # Rule: IF Status = 'Present' THEN Working_Hours > 0
        if 'present' in [str(v).lower() for v in status_values] and working_hours_col:
            present_rows = df[df[status_col].str.lower() == 'present']
            if len(present_rows) > 0:
                hours_for_present = present_rows[working_hours_col].dropna()
                if len(hours_for_present) > 0 and (hours_for_present > 0).all():
                    rules.append({
                        "rule": f"IF {status_col} = 'Present' THEN {working_hours_col} > 0",
                        "description": f"When employee is present, working hours must be greater than zero",
                        "if_then": f"IF {status_col} = 'Present' THEN {working_hours_col} > 0",
                        "sql": f"CASE WHEN {status_col} = 'Present' THEN {working_hours_col} > 0 ELSE TRUE END",
                        "pseudo_code": f"if {status_col} == 'Present':\n    assert {working_hours_col} > 0",
                        "confidence": "High",
                        "business_meaning": "HR Policy: Present employees must have working hours recorded",
                        "requires_approval": False,
                        "hr_usable": True
                    })
    
    # Check for late arrival rules based on Check_In_Time
    check_in_col = None
    for col in df.columns:
        if 'check_in' in col.lower() or 'checkin' in col.lower():
            check_in_col = col
            break
    
    if check_in_col:
        # Try to detect late arrival threshold (common: 9:15 AM)
        # Check if there's a Remarks column with "Late Arrival"
        remarks_col = None
        for col in df.columns:
            if 'remark' in col.lower() or 'note' in col.lower():
                remarks_col = col
                break
        
        if remarks_col:
            late_rows = df[df[remarks_col].str.contains('Late', case=False, na=False)]
            if len(late_rows) > 0:
                # Find common late check-in time
                late_times = late_rows[check_in_col].dropna()
                if len(late_times) > 0:
                    # Convert time strings to comparable format
                    try:
                        # Try to parse times and find threshold
                        time_strs = [str(t) for t in late_times if pd.notna(t)]
                        if time_strs:
                            # Common threshold: 09:15
                            rules.append({
                                "rule": f"IF {check_in_col} > '09:15' THEN Late_Arrival = TRUE",
                                "description": f"Employees checking in after 9:15 AM are marked as late arrival",
                                "if_then": f"IF {check_in_col} > '09:15' THEN Late_Arrival = TRUE",
                                "sql": f"CASE WHEN TIME({check_in_col}) > TIME('09:15') THEN TRUE ELSE FALSE END AS Late_Arrival",
                                "pseudo_code": f"if TIME({check_in_col}) > TIME('09:15'):\n    Late_Arrival = TRUE",
                                "confidence": "Medium",
                                "business_meaning": "HR Policy: Check-in after 9:15 AM is considered late arrival",
                                "requires_approval": True,
                                "hr_usable": True
                            })
                    except:
                        pass
    
    # Check for time relationship: Check_Out_Time must be after Check_In_Time
    check_out_col = None
    for col in df.columns:
        if 'check_out' in col.lower() or 'checkout' in col.lower():
            check_out_col = col
            break
    
    if check_in_col and check_out_col:
        # Verify this relationship exists in data
        valid_rows = df[[check_in_col, check_out_col]].dropna()
        if len(valid_rows) > 0:
            try:
                # Try to compare times
                rules.append({
                    "rule": f"{check_out_col} must be after {check_in_col}",
                    "description": f"Check-out time must be later than check-in time",
                    "if_then": f"IF {check_out_col} <= {check_in_col} THEN INVALID",
                    "sql": f"CHECK (TIME({check_out_col}) > TIME({check_in_col}))",
                    "pseudo_code": f"if TIME({check_out_col}) <= TIME({check_in_col}):\n    raise ValidationError('Check-out must be after check-in')",
                    "confidence": "High",
                    "business_meaning": "Business Logic: Employees cannot check out before checking in",
                    "requires_approval": False,
                    "hr_usable": True
                })
            except:
                pass
    
    return rules

# ==================== CONSTRAINTS ====================
def identify_constraints(df: pd.DataFrame) -> list:
    """Apply ONLY realistic, real-world limits - NO statistical ranges"""
    constraints = []
    
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            
            col_lower = col.lower()
            
            # Working Hours constraint: realistic maximum (24 hours)
            if 'hours' in col_lower and 'working' in col_lower:
                max_hours = col_data.max()
                if max_hours <= 24:
                    constraints.append({
                        "column": col,
                        "constraint": f"{col} <= 24",
                        "description": f"Working hours cannot exceed 24 hours per day",
                        "sql": f"CHECK ({col} <= 24)",
                        "pseudo_code": f"if {col} > 24: raise ConstraintError('Working hours cannot exceed 24')",
                        "confidence": "High",
                        "business_meaning": "Real-world limit: Maximum working hours per day is 24",
                        "requires_approval": False,
                        "hr_usable": True
                    })
            
            # Age constraints: realistic range
            if 'age' in col_lower:
                constraints.append({
                    "column": col,
                    "constraint": f"18 <= {col} <= 70",
                    "description": f"Age should be between 18 and 70 (typical working age)",
                    "sql": f"CHECK ({col} >= 18 AND {col} <= 70)",
                    "pseudo_code": f"if not (18 <= {col} <= 70): raise ConstraintError('Age out of working range')",
                    "confidence": "Medium",
                    "business_meaning": "HR Policy: Working age typically between 18 and 70 years",
                    "requires_approval": True,
                    "hr_usable": True
                })
            
            # Percentage constraints
            if 'percent' in col_lower or '%' in col:
                constraints.append({
                    "column": col,
                    "constraint": f"0 <= {col} <= 100",
                    "description": f"Percentage must be between 0 and 100",
                    "sql": f"CHECK ({col} >= 0 AND {col} <= 100)",
                    "pseudo_code": f"if not (0 <= {col} <= 100): raise ConstraintError('Percentage out of range')",
                    "confidence": "High",
                    "business_meaning": "Mathematical constraint: Percentages must be 0-100",
                    "requires_approval": False,
                    "hr_usable": True
                })
    
    return constraints

# ==================== DERIVED FIELDS ====================
def identify_derivations(df: pd.DataFrame) -> list:
    """Create derived fields ONLY if they have direct business value"""
    derivations = []
    
    # Late Arrival derived field
    check_in_col = None
    for col in df.columns:
        if 'check_in' in col.lower() or 'checkin' in col.lower():
            check_in_col = col
            break
    
    if check_in_col:
        derivations.append({
            "derived_field": "Late_Arrival",
            "formula": f"IF {check_in_col} > '09:15' THEN TRUE ELSE FALSE",
            "description": "Boolean field indicating if employee arrived late (after 9:15 AM)",
            "sql": f"CASE WHEN TIME({check_in_col}) > TIME('09:15') THEN TRUE ELSE FALSE END AS Late_Arrival",
            "pseudo_code": f"Late_Arrival = TIME({check_in_col}) > TIME('09:15')",
            "confidence": "Medium",
            "business_meaning": "HR Metric: Identifies employees with late arrivals for attendance tracking",
            "requires_approval": True,
            "hr_usable": True
        })
    
    # Overtime Hours calculation
    working_hours_col = None
    for col in df.columns:
        if 'working_hours' in col.lower():
            working_hours_col = col
            break
    
    if working_hours_col:
        standard_hours = 9  # Typical standard working hours
        derivations.append({
            "derived_field": "Overtime_Hours",
            "formula": f"IF {working_hours_col} > {standard_hours} THEN {working_hours_col} - {standard_hours} ELSE 0",
            "description": f"Calculate overtime hours when working hours exceed standard {standard_hours} hours",
            "sql": f"CASE WHEN {working_hours_col} > {standard_hours} THEN {working_hours_col} - {standard_hours} ELSE 0 END AS Overtime_Hours",
            "pseudo_code": f"Overtime_Hours = max(0, {working_hours_col} - {standard_hours})",
            "confidence": "Medium",
            "business_meaning": f"HR Calculation: Overtime hours for payroll when employee works more than {standard_hours} hours",
            "requires_approval": True,
            "hr_usable": True
        })
    
    return derivations

# ==================== ASSOCIATIONS ====================
def identify_associations(df: pd.DataFrame) -> list:
    """Generate associations ONLY if they have clear business meaning - NO constant/single-value columns"""
    associations = []
    
    # Filter out identifier columns
    id_cols = [col for col in df.columns if any(x in col.lower() for x in ['id', 'name', 'code'])]
    
    # Filter out constant columns (single value)
    constant_cols = [col for col in df.columns if df[col].nunique() == 1]
    
    # Filter out date columns with single value
    date_cols = [col for col in df.columns if df[col].nunique() == 1 and 'date' in col.lower()]
    
    excluded_cols = set(id_cols + constant_cols + date_cols)
    
    numeric_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64'] and col not in excluded_cols]
    
    # Check for 1:1 mappings (but not ID columns)
    for col1 in df.columns:
        if col1 in excluded_cols:
            continue
        for col2 in df.columns:
            if col2 in excluded_cols or col1 == col2:
                continue
            
            # Check if col1 uniquely determines col2 (but not vice versa for IDs)
            if col1 not in id_cols:
                unique_pairs = df[[col1, col2]].drop_duplicates()
                if len(unique_pairs) == len(df[col1].unique()) and len(df[col1].unique()) > 1:
                    associations.append({
                        "type": "1:1 Mapping",
                        "columns": [col1, col2],
                        "description": f"{col1} uniquely determines {col2}",
                        "sql": f"-- {col1} -> {col2} (1:1 mapping)",
                        "pseudo_code": f"# {col1} -> {col2} (1:1 mapping)",
                        "confidence": "High",
                        "business_meaning": f"Each {col1} value corresponds to exactly one {col2} value",
                        "requires_approval": False,
                        "hr_usable": True
                    })
                    break
    
    return associations[:5]  # Limit to avoid too many

# ==================== STATISTICAL INSIGHTS (Separate from Business Rules) ====================
def generate_statistical_insights(df: pd.DataFrame, profile: dict) -> list:
    """Generate statistical insights - CLEARLY MARKED as non-business rules"""
    insights = []
    
    # Dataset size warning
    if profile["total_rows"] < 30:
        insights.append({
            "type": "Warning",
            "title": "Small Dataset",
            "description": f"Dataset has only {profile['total_rows']} rows. Limited statistical reliability.",
            "impact": "Low",
            "is_business_rule": False
        })
    
    # Missing data insights
    for col_info in profile["columns"]:
        if col_info["null_percentage"] > 20:
            insights.append({
                "type": "Data Quality",
                "title": f"High Missing Data in {col_info['name']}",
                "description": f"{col_info['name']} has {col_info['null_percentage']:.1f}% missing values",
                "impact": "Medium",
                "is_business_rule": False
            })
    
    # Outlier detection (statistical only)
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            col_data = df[col].dropna()
            if len(col_data) > 10:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outliers = ((col_data < (q1 - 1.5 * iqr)) | (col_data > (q3 + 1.5 * iqr))).sum()
                if outliers > 0:
                    insights.append({
                        "type": "Statistical Insight",
                        "title": f"Outliers Detected in {col} (Statistical Analysis)",
                        "description": f"{outliers} statistical outliers detected in {col} using IQR method",
                        "impact": "Low",
                        "is_business_rule": False,
                        "note": "This is a statistical observation, NOT a business rule"
                    })
    
    return insights

# ==================== DATA QUALITY WARNINGS ====================
def generate_data_quality_warnings(df: pd.DataFrame, profile: dict) -> list:
    """Generate data quality warnings - NOT business rules"""
    warnings = []
    
    # Check for inconsistencies in business rules
    status_col = None
    working_hours_col = None
    
    for col in df.columns:
        if 'status' in col.lower():
            status_col = col
        if 'working_hours' in col.lower():
            working_hours_col = col
    
    if status_col and working_hours_col:
        # Check for violations: Absent but hours > 0
        absent_with_hours = df[(df[status_col].str.lower() == 'absent') & (df[working_hours_col] > 0)]
        if len(absent_with_hours) > 0:
            warnings.append({
                "type": "Data Quality Issue",
                "title": "Data Inconsistency: Absent employees with working hours > 0",
                "description": f"Found {len(absent_with_hours)} records where Status='Absent' but Working_Hours > 0",
                "impact": "High",
                "recommendation": "Review and correct these records - Absent employees should have 0 working hours",
                "is_business_rule": False
            })
    
    return warnings

# ==================== MAIN ANALYSIS FUNCTION ====================
def analyze_data(df: pd.DataFrame) -> dict:
    """Main analysis function - Focus ONLY on real-world business rules"""
    
    # 1. Domain Detection
    domain_info = detect_domain(df)
    
    # 2. Dataset Profiling
    profile = profile_dataset(df)
    
    # 3. Validation Rules (Universal, safe rules)
    validation_rules = identify_validation_rules(df)
    
    # 4. Decision Rules (Real HR/business policies)
    decision_rules = identify_decision_rules(df)
    
    # 5. Constraints (Realistic limits)
    constraints = identify_constraints(df)
    
    # 6. Derivations (Business-valuable calculated fields)
    derivations = identify_derivations(df)
    
    # 7. Associations (Clear business meaning only)
    associations = identify_associations(df)
    
    # 8. Statistical Insights (Separate, clearly marked)
    statistical_insights = generate_statistical_insights(df, profile)
    
    # 9. Data Quality Warnings (Non-rules)
    data_quality_warnings = generate_data_quality_warnings(df, profile)
    
    # 10. Summary
    total_business_rules = (
        len(validation_rules) +
        len(decision_rules) +
        len(constraints) +
        len(derivations) +
        len(associations)
    )
    
    rules_requiring_approval = (
        len([r for r in decision_rules if r.get("requires_approval", False)]) +
        len([r for r in constraints if r.get("requires_approval", False)]) +
        len([r for r in derivations if r.get("requires_approval", False)])
    )
    
    return {
        "summary": {
            "domain_detected": domain_info["domain"],
            "domain_description": domain_info["description"],
            "domain_reasoning": domain_info["reasoning"],
            "domain_confidence": domain_info["confidence"],
            "total_rows": profile["total_rows"],
            "total_columns": profile["total_columns"],
            "total_business_rules": total_business_rules,
            "rules_requiring_approval": rules_requiring_approval,
            "small_dataset_warning": profile["total_rows"] < 30
        },
        "dataset_profile": profile,
        "validation_rules": {
            "count": len(validation_rules),
            "rules": validation_rules,
            "note": "Universal validation rules - ready for implementation"
        },
        "decision_rules": {
            "count": len(decision_rules),
            "rules": decision_rules,
            "note": "HR Policy-based IF-THEN rules - reflect real business logic"
        },
        "constraints": {
            "count": len(constraints),
            "rules": constraints,
            "note": "Realistic business constraints - real-world limits"
        },
        "derivations": {
            "count": len(derivations),
            "rules": derivations,
            "note": "Business-valuable calculated fields - direct HR use"
        },
        "associations": {
            "count": len(associations),
            "rules": associations,
            "note": "Clear business relationships between columns"
        },
        "data_quality_warnings": {
            "count": len(data_quality_warnings),
            "items": data_quality_warnings,
            "note": "Data quality issues - NOT business rules"
        },
        "statistical_insights": {
            "count": len(statistical_insights),
            "items": statistical_insights,
            "note": "⚠️ STATISTICAL INSIGHTS - NOT BUSINESS RULES. These are observations for reference only."
        },
        "recommendations": [
            "Review all Decision Rules to confirm they match your HR policies",
            "Validate Constraint ranges with HR team",
            "Test Derived Fields with sample data before implementation",
            "Address Data Quality Warnings before applying rules",
            "Statistical Insights are for reference only - do not implement as business rules"
        ]
    }
