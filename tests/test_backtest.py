"""Tests for strategy backtesting engine and performance calculations."""
import numpy as np
import pandas as pd
import pytest

from quantpulse.backtest.engine import BacktestEngine
from quantpulse.backtest.performance import calculate_financial_metrics


def test_calculate_financial_metrics():
    equity = pd.Series([10000.0, 10200.0, 10100.0, 10500.0, 10400.0])
    benchmark = pd.Series([10000.0, 9900.0, 9800.0, 10100.0, 10000.0])
    bar_returns = equity.pct_change().dropna()
    trades_pnl = [0.02, -0.01, 0.04, -0.01]

    metrics = calculate_financial_metrics(equity, benchmark, bar_returns, trades_pnl)

    assert metrics["strategy_return"] == pytest.approx(0.04, rel=1e-3)
    assert metrics["benchmark_return"] == pytest.approx(0.00, rel=1e-3)
    assert metrics["alpha"] == pytest.approx(0.04, rel=1e-3)
    assert metrics["max_drawdown"] >= 0.0
    assert metrics["win_rate"] == 0.5
    assert metrics["trade_count"] == 4


def test_backtest_engine_run():
    # 20 bars with alternating signals
    prices = [100.0 + i for i in range(20)]
    signals = [1, 2, 1, 1, 0, 1, 2, 1, 0, 1, 1, 2, 1, 0, 1, 1, 2, 1, 0, 1]
    df = pd.DataFrame({"price": prices, "signal": signals, "close": prices})

    engine = BacktestEngine(fee_rate=0.001, slippage_rate=0.0005, initial_capital=10000.0)
    res = engine.run(df, signal_col="signal")

    assert res.initial_capital == 10000.0
    assert res.final_capital > 0.0
    assert len(res.trades) > 0
    assert "strategy_return" in res.metrics
    assert "sharpe_ratio" in res.metrics
    assert len(res.equity_df) == 20
