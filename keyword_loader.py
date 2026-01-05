"""
Keyword Loader - Extracts HR domain keywords from the .md file
"""
import re
from typing import List, Dict, Set

def load_hr_keywords(file_path: str = ".md") -> Dict[str, List[str]]:
    """
    Load HR keywords from the .md file and organize by category
    Returns a dictionary with category names and their keywords
    """
    # Try to find the file in the same directory as this script
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, file_path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # If file not found, return default keywords
        return get_default_keywords()
    
    keywords = {}
    current_category = None
    all_keywords = []
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip header line
        if 'HR DOMAIN' in line.upper() or 'KEYWORDS LIST' in line.upper():
            continue
        
        # Detect category headers - lines starting with number/emoji followed by text
        # Pattern: "1️⃣ Employee Basic Details" or "1 Employee Basic Details"
        if re.match(r'^[\d1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟]+\s+', line) or re.match(r'^\d+[️⃣\s]', line):
            # Extract category name - text after number/emoji
            category_text = re.sub(r'^[\d1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟\s/–-]+', '', line).strip()
            # Remove anything in parentheses
            category_text = re.sub(r'\s*\([^)]*\)\s*', '', category_text).strip()
            if category_text:
                current_category = category_text
                if current_category not in keywords:
                    keywords[current_category] = []
            continue
        
        # Skip lines with parentheses only (descriptions)
        if line.startswith('(') and line.endswith(')'):
            continue
        
        # Extract keywords - simple lowercase words with underscores, no special chars at start
        # Keywords in the file are just the words themselves on separate lines
        if line and not line.startswith('#') and len(line) < 50:
            # Clean the keyword
            keyword = line.strip().lower()
            # Replace spaces/hyphens with underscores
            keyword = keyword.replace(' ', '_').replace('-', '_')
            # Remove anything in parentheses (like "(Full-time / Part-time / Contract)")
            keyword = re.sub(r'\([^)]*\)', '', keyword).strip()
            # Remove special characters except underscore
            keyword = re.sub(r'[^a-z0-9_]', '', keyword)
            
            # Validate keyword (must have at least 2 characters, not just numbers)
            if keyword and len(keyword) >= 2 and not keyword.isdigit():
                if current_category:
                    if keyword not in keywords[current_category]:
                        keywords[current_category].append(keyword)
                    if keyword not in all_keywords:
                        all_keywords.append(keyword)
                else:
                    # Add to general category
                    if 'General' not in keywords:
                        keywords['General'] = []
                    if keyword not in keywords['General']:
                        keywords['General'].append(keyword)
                    if keyword not in all_keywords:
                        all_keywords.append(keyword)
    
    # Flatten all keywords into a single list for easy matching
    keywords['ALL'] = all_keywords  # Already deduplicated
    
    return keywords if keywords.get('ALL') else get_default_keywords()

def get_default_keywords() -> Dict[str, List[str]]:
    """Return default HR keywords if file cannot be loaded"""
    return {
        'ALL': [
            'employee_id', 'emp_id', 'employee_name', 'first_name', 'last_name',
            'gender', 'date_of_birth', 'dob', 'age', 'marital_status', 'nationality',
            'department', 'team', 'designation', 'role', 'job_title', 'position',
            'employment_type', 'joining_date', 'date_of_joining', 'probation_period',
            'attendance', 'attendance_percentage', 'present_days', 'absent_days',
            'working_days', 'check_in', 'check_out', 'punch_in', 'punch_out',
            'late_days', 'early_exit', 'shift', 'overtime_hours',
            'leave_days', 'leave_type', 'sick_leave', 'casual_leave', 'earned_leave',
            'paid_leave', 'unpaid_leave', 'leave_balance', 'leave_applied',
            'leave_approved', 'leave_rejected',
            'salary', 'basic_salary', 'gross_salary', 'net_salary', 'hra', 'allowance',
            'bonus', 'incentive', 'deduction', 'tax', 'pf', 'esi', 'payroll_month',
            'performance_score', 'performance_rating', 'appraisal', 'review', 'kpi',
            'productivity', 'efficiency', 'target', 'achievement', 'feedback',
            'risk', 'risk_level', 'attrition', 'attrition_flag', 'churn', 'warning',
            'status', 'employee_status',
            'late_marks', 'warning_count', 'misconduct', 'compliance',
            'policy_violation', 'disciplinary_action',
            'skill', 'skills', 'training', 'training_hours', 'certification',
            'experience', 'years_of_experience', 'upskilling',
            'manager', 'reporting_manager', 'supervisor', 'location', 'branch',
            'work_location', 'shift_type', 'work_mode'
        ]
    }

def match_keywords_in_columns(columns: List[str], keywords: List[str]) -> List[str]:
    """
    Match dataset columns against HR keywords
    Returns list of matched keywords
    """
    matched = []
    columns_lower = [col.lower().strip() for col in columns]
    
    for keyword in keywords:
        # Direct match
        for col in columns_lower:
            if keyword == col or keyword in col or col in keyword:
                if keyword not in matched:
                    matched.append(keyword)
                    break
    
    return matched

