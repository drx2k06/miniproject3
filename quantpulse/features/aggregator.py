"""Tick-to-bar time and volume resampling."""
from __future__ import annotations

import numpy as np
import pandas as pd


def to_bars(trades: pd.DataFrame, sec: int = 1) -> pd.DataFrame:
    """Group trade events into uniform time bars.

    Preserves full OHLC, buy/sell volume separation, and trade counts.
    Ensures backward compatibility with crypto.py expected columns:
    ['timestamp', 'price', 'qty', 'buy', 'n'] plus ['open', 'high', 'low', 'close', 'sell'].
    """
    if trades.empty:
        return pd.DataFrame(
            columns=["timestamp", "price", "open", "high", "low", "close", "qty", "buy", "sell", "n"]
        )

    d = trades.copy()
    if not np.issubdtype(d["timestamp"].dtype, np.datetime64):
        d["timestamp"] = pd.to_datetime(d["timestamp"])

    d["buy"] = np.where(d["side"].str.lower() == "buy", d["quantity"], 0.0)
    d["sell"] = np.where(d["side"].str.lower() == "sell", d["quantity"], 0.0)

    # Resample using pandas time rule
    rule = f"{max(sec, 1)}s"
    g = d.set_index("timestamp").resample(rule)

    b = pd.DataFrame({
        "open": g["price"].first(),
        "high": g["price"].max(),
        "low": g["price"].min(),
        "close": g["price"].last(),
        "price": g["price"].last(),  # backward compatibility alias
        "qty": g["quantity"].sum(),
        "buy": g["buy"].sum(),
        "sell": g["sell"].sum(),
        "n": g["price"].count(),
    })

    # Keep only active bars where trades actually occurred
    bars = b[b["n"] > 0].reset_index()
    return bars
