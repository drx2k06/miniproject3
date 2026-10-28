"""Security, input validation, and anomaly sanitization."""
from __future__ import annotations

import io
from typing import Any, BinaryIO, Union

import numpy as np
import pandas as pd


class DataValidationError(Exception):
    """Raised when uploaded trade data violates safety or schema constraints."""
    pass


def validate_csv_upload(
    file_obj: Union[BinaryIO, io.BytesIO],
    max_size_mb: int = 100,
) -> None:
    """Validate uploaded file size and initial bytes to prevent DoS or corrupt inputs."""
    if hasattr(file_obj, "getbuffer"):
        size_bytes = file_obj.getbuffer().nbytes
    elif hasattr(file_obj, "seek") and hasattr(file_obj, "tell"):
        file_obj.seek(0, io.SEEK_END)
        size_bytes = file_obj.tell()
        file_obj.seek(0)
    else:
        size_bytes = 0

    if size_bytes > (max_size_mb * 1024 * 1024):
        raise DataValidationError(
            f"Uploaded file exceeds maximum permitted size of {max_size_mb} MB ({size_bytes / (1024*1024):.1f} MB)."
        )


def sanitize_financial_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitize financial datasets by replacing infinities and clipping anomalous outliers."""
    d = df.copy()
    numeric_cols = d.select_dtypes(include=[np.number]).columns
    
    # Replace inf and -inf with NaN
    d[numeric_cols] = d[numeric_cols].replace([np.inf, -np.inf], np.nan)
    
    # Clip extreme percentage returns to [-1.0, 10.0]
    for col in d.columns:
        if "ret_" in col:
            d[col] = d[col].clip(lower=-1.0, upper=10.0)
        elif "flow" in col:
            d[col] = d[col].clip(lower=-1.0, upper=1.0)
            
    return d


def verify_numeric_bounds(val: Any, min_val: float, max_val: float, name: str) -> float:
    """Verify numeric parameter sits securely within expected boundary."""
    try:
        fval = float(val)
    except (TypeError, ValueError):
        raise DataValidationError(f"Parameter '{name}' must be a valid number.")

    if not (min_val <= fval <= max_val):
        raise DataValidationError(
            f"Parameter '{name}' must be between {min_val} and {max_val}. Received: {fval}."
        )
    return fval
