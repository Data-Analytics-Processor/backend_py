"""The toolset for relational statistical tools like correlation coefficient, relational matrix, etc. """

import pandas as pd
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool

@tool
def get_correlation_matrix(file_path: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calculates the Pearson correlation coefficient between numeric columns.
    Use this to find relationships between variables (e.g. 'Does age correlate with salary?').
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Filter columns if specified
        if columns:
            missing = [c for c in columns if c not in df.columns]
            if missing:
                return {"error": f"Columns not found: {missing}"}
            df = df[columns]
            
        # Select only numeric columns for correlation
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return {"error": "No numeric columns found for correlation."}

        return numeric_df.corr().fillna(0).to_dict()
    except Exception as e:
        return {"error": str(e)}