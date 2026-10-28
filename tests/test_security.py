"""Tests for input validation, sanitization, and security boundaries."""
import io
import numpy as np
import pandas as pd
import pytest

from quantpulse.security.validator import (
    DataValidationError,
    sanitize_financial_dataframe,
    validate_csv_upload,
    verify_numeric_bounds,
)


def test_validate_csv_upload_size_limit():
    # 2MB stream with 1MB limit
    large_stream = io.BytesIO(b"0" * (2 * 1024 * 1024))
    with pytest.raises(DataValidationError, match="exceeds maximum permitted size"):
        validate_csv_upload(large_stream, max_size_mb=1)


def test_sanitize_financial_dataframe():
    df = pd.DataFrame({
        "ret_1": [0.01, np.inf, -np.inf, 25.0, -0.99],
        "flow": [0.5, 5.0, -5.0, 0.0, np.nan],
    })
    cleaned = sanitize_financial_dataframe(df)

    # Infs replaced by NaN
    assert not np.isinf(cleaned["ret_1"].dropna()).any()
    # Clipped
    assert cleaned["ret_1"].max() <= 10.0
    assert cleaned["ret_1"].min() >= -1.0
    assert cleaned["flow"].max() <= 1.0
    assert cleaned["flow"].min() >= -1.0


def test_verify_numeric_bounds():
    assert verify_numeric_bounds(10.0, 0.0, 100.0, "risk") == 10.0

    with pytest.raises(DataValidationError, match="must be between"):
        verify_numeric_bounds(150.0, 0.0, 100.0, "risk")

    with pytest.raises(DataValidationError, match="valid number"):
        verify_numeric_bounds("invalid_num", 0.0, 100.0, "risk")
