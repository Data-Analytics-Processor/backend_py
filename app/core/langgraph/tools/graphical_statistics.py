"""The toolset for graphical statistical tools like normal distribution, binomial distribuion etc. """

import pandas as pd
import numpy as np
from typing import Dict, Any
from langchain_core.tools import tool

@tool
def get_normal_distribution(file_path: str, column: str, points: int = 100) -> Dict[str, Any]:
    """
    Generates data for a normal (Gaussian) distribution curve and histogram for a specific column.
    Returns JSON with 'curve' (x, y coordinates) and 'histogram' (bins, density).
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        if column not in df.columns:
            return {"error": f"Column '{column}' not found."}

        series = df[column].dropna()

        if not np.issubdtype(series.dtype, np.number):
            return {"error": f"Column '{column}' is not numeric."}

        mean = float(series.mean())
        std = float(series.std())

        # Generate x range for the bell curve
        x = np.linspace(series.min(), series.max(), points)

        # Normal distribution PDF formula
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(
            -0.5 * ((x - mean) / std) ** 2
        )

        # Histogram data
        hist_counts, hist_bins = np.histogram(series, bins=20, density=True)

        return {
            "column": column,
            "mean": mean,
            "std_dev": std,
            "curve": {
                "x": x.tolist(),
                "y": y.tolist()
            },
            "histogram": {
                "bins": hist_bins.tolist(),
                "density": hist_counts.tolist()
            }
        }
    except Exception as e:
        return {"error": str(e)}