"""Microstructure and technical indicator calculations."""
from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_microstructure_flow(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate order-flow imbalance, cumulative volume delta, and log volume."""
    d = df.copy()
    qty_safe = np.where(d["qty"] > 0, d["qty"], 1e-8)
    # Order Flow Imbalance bounded [-1.0, 1.0]
    flow = 2.0 * d["buy"] / qty_safe - 1.0
    d["flow"] = np.clip(flow, -1.0, 1.0)
    d["flow_5"] = d["flow"].rolling(5, min_periods=1).mean()
    d["flow_20"] = d["flow"].rolling(20, min_periods=1).mean()
    
    # Cumulative Volume Delta (CVD)
    delta = d["buy"] - d["sell"] if "sell" in d.columns else (2.0 * d["buy"] - d["qty"])
    d["cvd"] = delta.cumsum()
    d["log_qty"] = np.log1p(d["qty"])
    return d


def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Volume-Weighted Average Price and relative distance."""
    d = df.copy()
    price = d["close"] if "close" in d.columns else d["price"]
    cum_pv = (price * d["qty"]).cumsum()
    cum_vol = d["qty"].cumsum().replace(0, 1e-8)
    d["vwap"] = cum_pv / cum_vol
    d["vwap_dist"] = (price - d["vwap"]) / d["vwap"]
    return d


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate Relative Strength Index (RSI) using Wilder's smoothing."""
    d = df.copy()
    price = d["close"] if "close" in d.columns else d["price"]
    delta = price.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, 1e-8)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    d[f"rsi_{period}"] = rsi.fillna(50.0)
    return d


def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Calculate Moving Average Convergence Divergence (MACD)."""
    d = df.copy()
    price = d["close"] if "close" in d.columns else d["price"]
    ema_fast = price.ewm(span=fast, adjust=False).mean()
    ema_slow = price.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - macd_signal
    
    d["macd_line"] = macd_line
    d["macd_signal"] = macd_signal
    d["macd_hist"] = macd_hist
    return d


def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
) -> pd.DataFrame:
    """Calculate Bollinger Bands, %B, and normalized band width."""
    d = df.copy()
    price = d["close"] if "close" in d.columns else d["price"]
    sma = price.rolling(period, min_periods=1).mean()
    rolling_std = price.rolling(period, min_periods=1).std().fillna(1e-8)
    
    upper = sma + (std_dev * rolling_std)
    lower = sma - (std_dev * rolling_std)
    width = (upper - lower) / sma.replace(0, 1e-8)
    
    band_range = (upper - lower).replace(0, 1e-8)
    pct_b = (price - lower) / band_range
    
    d["bb_upper"] = upper
    d["bb_lower"] = lower
    d["bb_pct_b"] = np.clip(pct_b, -0.5, 1.5)
    d["bb_width"] = width
    return d
