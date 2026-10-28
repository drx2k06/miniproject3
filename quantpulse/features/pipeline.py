"""End-to-end feature pipeline execution."""
from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from quantpulse.features.indicators import (
    calculate_bollinger_bands,
    calculate_macd,
    calculate_microstructure_flow,
    calculate_rsi,
    calculate_vwap,
)


def compute_features(
    bars: pd.DataFrame,
    mode: Literal["full", "baseline"] = "full",
) -> pd.DataFrame:
    """Compute comprehensive microstructure and technical indicators for bar series."""
    if bars.empty:
        return bars.copy()

    b = bars.copy()
    price = b["close"] if "close" in b.columns else b["price"]

    # Returns across multiple horizons
    b["ret_1"] = price.pct_change().fillna(0.0)
    b["ret_5"] = price.pct_change(5).fillna(0.0)
    b["ret_10"] = price.pct_change(10).fillna(0.0)
    b["ret_20"] = price.pct_change(20).fillna(0.0)

    # Volatility measures
    b["vol_20"] = b["ret_1"].rolling(20, min_periods=2).std().fillna(0.0)
    b["vol_60"] = b["ret_1"].rolling(60, min_periods=2).std().fillna(0.0)

    # Order flow imbalance & volume features
    b = calculate_microstructure_flow(b)

    if mode == "full":
        b = calculate_vwap(b)
        b = calculate_rsi(b, period=14)
        b = calculate_macd(b, fast=12, slow=26, signal=9)
        b = calculate_bollinger_bands(b, period=20, std_dev=2.0)

    return b


def features(bars: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible wrapper matching original crypto.py signature."""
    b = bars.copy()
    price = b["close"] if "close" in b.columns else b["price"]
    b["ret_1"] = price.pct_change()
    b["ret_5"] = price.pct_change(5)
    b["vol_20"] = b["ret_1"].rolling(20).std()
    b["flow"] = 2.0 * b["buy"] / b["qty"].replace(0, 1e-8) - 1.0
    b["flow_5"] = b["flow"].rolling(5).mean()
    b["log_qty"] = np.log1p(b["qty"])
    return b
