"""Configuration management for QuantPulse."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


@dataclass
class QuantConfig:
    """System configuration parameters with environment variable overrides."""
    
    # Network & API
    binance_base_url: str = os.getenv("BINANCE_BASE", "https://data-api.binance.vision")
    symbol: str = os.getenv("SYMBOL", "BTCUSDT")
    api_timeout_seconds: int = int(os.getenv("API_TIMEOUT", "10"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Data & Sampling
    default_bar_seconds: int = int(os.getenv("BAR_SECONDS", "1"))
    default_data_file: str = os.getenv("DATA_FILE", "BTCUSDT-trades.csv")
    
    # Model & Labeling
    predict_ahead_bars: int = int(os.getenv("PREDICT_AHEAD", "10"))
    tail_quantile: float = float(os.getenv("TAIL_QUANTILE", "0.25"))
    test_split_ratio: float = float(os.getenv("TEST_SPLIT", "0.30"))
    random_seed: int = 42
    
    # Backtest & Trading Frictions
    default_taker_fee: float = float(os.getenv("TAKER_FEE", "0.00075"))  # 0.075%
    default_slippage: float = float(os.getenv("SLIPPAGE", "0.00050"))    # 5 bps
    initial_paper_cash: float = float(os.getenv("PAPER_CASH", "10000.0"))
    default_risk_pct: float = float(os.getenv("RISK_PCT", "10.0"))
    
    # Feature Definitions
    baseline_features: List[str] = field(default_factory=lambda: [
        "ret_1", "ret_5", "vol_20", "flow", "flow_5", "log_qty"
    ])
    
    full_features: List[str] = field(default_factory=lambda: [
        "ret_1", "ret_5", "ret_10", "ret_20",
        "vol_20", "vol_60",
        "flow", "flow_5", "flow_20", "cvd", "log_qty",
        "vwap_dist", "rsi_14", "macd_line", "macd_signal", "macd_hist",
        "bb_pct_b", "bb_width"
    ])
    
    # Target Classes
    label_names: dict = field(default_factory=lambda: {0: "SELL", 1: "HOLD", 2: "BUY"})


default_config = QuantConfig()
