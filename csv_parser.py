"""
Robust CSV Parser - Handles various CSV parsing errors gracefully
"""
import pandas as pd
from io import BytesIO
from typing import Optional

def parse_csv_robust(contents: bytes) -> pd.DataFrame:
    """
    Robust CSV parsing that handles various error cases:
    - Inconsistent field counts
    - Unquoted fields with commas
    - Encoding issues
    - Malformed lines
    """
    # Try 1: Standard CSV parsing
    try:
        return pd.read_csv(BytesIO(contents))
    except pd.errors.ParserError:
        pass
    
    # Try 2: Skip bad lines (pandas 1.3.0+)
    try:
        return pd.read_csv(BytesIO(contents), on_bad_lines='skip', engine='python')
    except (pd.errors.ParserError, TypeError):
        pass
    
    # Try 3: Warn on bad lines and continue
    try:
        return pd.read_csv(BytesIO(contents), on_bad_lines='warn', engine='python')
    except (pd.errors.ParserError, TypeError):
        pass
    
    # Try 4: Python engine with skip bad lines (most forgiving)
    try:
        return pd.read_csv(BytesIO(contents), sep=',', on_bad_lines='skip', engine='python', quoting=1)
    except Exception:
        pass
    
    # Try 5: Python engine with skip initial space and flexible quoting
    try:
        return pd.read_csv(BytesIO(contents), sep=',', skipinitialspace=True, 
                          on_bad_lines='skip', engine='python', 
                          quotechar='"', quoting=1, escapechar=None)
    except Exception:
        pass
    
    # Try 6: Last resort - try with different encoding
    try:
        contents_str = contents.decode('utf-8', errors='replace')
        return pd.read_csv(BytesIO(contents_str.encode('utf-8')), 
                          on_bad_lines='skip', engine='python')
    except Exception as e:
        raise ValueError(f"Unable to parse CSV file. Please check that:\n"
                        f"1. All fields with commas are properly quoted\n"
                        f"2. All lines have the same number of fields\n"
                        f"3. The file encoding is UTF-8\n"
                        f"Original error: {str(e)}")

