"""Forward return labeling for supervised cryptocurrency classification."""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


def create_labels(
    bars: pd.DataFrame,
    ahead: int = 10,
    tail: float = 0.25,
) -> Tuple[pd.DataFrame, float, float]:
    """Generate forward price return targets and 3-class categorical labels.

    Classes:
    0: SELL (future return is in bottom `tail` quantile)
    1: HOLD (future return is in middle (1 - 2*tail) quantile)
    2: BUY  (future return is in top `tail` quantile)

    Returns
    -------
    Tuple[pd.DataFrame, float, float]
        DataFrame with added 'future' and 'label' columns, plus the lo and hi thresholds.
    """
    b = bars.copy()
    price = b["close"] if "close" in b.columns else b["price"]
    b["future"] = price.shift(-ahead) / price - 1.0

    valid_future = b["future"].dropna()
    if valid_future.empty:
        b["label"] = 1
        return b, 0.0, 0.0

    lo, hi = valid_future.quantile([tail, 1.0 - tail])
    
    # 0: SELL, 1: HOLD, 2: BUY
    conditions = [b["future"] < lo, b["future"] > hi]
    choices = [0, 2]
    b["label"] = np.select(conditions, choices, default=1)
    
    return b, float(lo), float(hi)
