"""Financial performance metrics: Sharpe, Sortino, Drawdown, Profit Factor."""
from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd


def calculate_financial_metrics(
    equity_curve: pd.Series,
    benchmark_curve: pd.Series,
    bar_returns: pd.Series,
    trades_pnl: list[float],
    annualization_factor: float = 365 * 24 * 3600,  # 1-second bars annualized
) -> Dict[str, Any]:
    """Calculate institutional risk-adjusted return and drawdown statistics."""
    if equity_curve.empty or len(equity_curve) < 2:
        return {
            "strategy_return": 0.0,
            "benchmark_return": 0.0,
            "alpha": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "trade_count": 0,
        }

    start_eq = equity_curve.iloc[0]
    end_eq = equity_curve.iloc[-1]
    strat_ret = float((end_eq / start_eq) - 1.0) if start_eq > 0 else 0.0

    start_bm = benchmark_curve.iloc[0]
    end_bm = benchmark_curve.iloc[-1]
    bm_ret = float((end_bm / start_bm) - 1.0) if start_bm > 0 else 0.0
    alpha = strat_ret - bm_ret

    # Drawdown series
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_dd = float(abs(drawdown.min()))

    # Sharpe & Sortino (per-bar scaled)
    mean_ret = bar_returns.mean()
    std_ret = bar_returns.std()
    downside_std = bar_returns[bar_returns < 0].std()

    sharpe = float((mean_ret / std_ret) * np.sqrt(len(bar_returns))) if std_ret > 0 else 0.0
    sortino = float((mean_ret / downside_std) * np.sqrt(len(bar_returns))) if downside_std > 0 else 0.0

    # Trade level win-rate & profit factor
    trade_count = len(trades_pnl)
    if trade_count > 0:
        gains = [p for p in trades_pnl if p > 0]
        losses = [abs(p) for p in trades_pnl if p < 0]
        win_rate = float(len(gains) / trade_count)
        sum_loss = sum(losses)
        profit_factor = float(sum(gains) / sum_loss) if sum_loss > 0 else (99.0 if sum(gains) > 0 else 1.0)
    else:
        win_rate = 0.0
        profit_factor = 0.0

    return {
        "strategy_return": strat_ret,
        "benchmark_return": bm_ret,
        "alpha": alpha,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "trade_count": trade_count,
        "drawdown_series": drawdown,
    }
