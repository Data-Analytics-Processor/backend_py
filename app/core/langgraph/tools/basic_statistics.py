"""The toolset for basic statistical tools like mean, median, mode. """

import pandas as pd
from typing import Dict, Any, Optional
from langchain_core.tools import tool

@tool
def describe_dataset(file_path: str) -> Dict[str, Any]:
    """
    Calculates basic statistical summary (count, mean, std, min, max) for all columns in the dataset.
    Use this to get a general overview of the data.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        # fillna("") ensures JSON compatibility (NaN is not valid JSON)
        return df.describe(include="all").fillna("").to_dict()
    except Exception as e:
        return {"error": str(e)}