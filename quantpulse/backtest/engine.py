"""Event-driven and vectorized backtesting engine with realistic frictions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from quantpulse.backtest.performance import calculate_financial_metrics
from quantpulse.config import default_config


@dataclass
class BacktestResult:
    """Complete results from historical strategy simulation."""

    metrics: Dict[str, Any]
    equity_df: pd.DataFrame
    trades: List[Dict[str, Any]]
    initial_capital: float
    final_capital: float


class BacktestEngine:
    """Historical trading strategy simulation engine with fee and slippage modeling."""

    def __init__(
        self,
        fee_rate: float = default_config.default_taker_fee,
        slippage_rate: float = default_config.default_slippage,
        initial_capital: float = 10000.0,
    ):
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate
        self.initial_capital = initial_capital

    def run(
        self,
        bars: pd.DataFrame,
        signals: Optional[pd.Series | np.ndarray] = None,
        signal_col: str = "prediction",
    ) -> BacktestResult:
        """Execute historical backtest on test bar series.

        Signals:
        2: Long (BUY)
        1: Hold existing position
        0: Neutral / Flat (SELL / CASH)
        """
        df = bars.copy().reset_index(drop=True)
        if signals is not None:
            df["signal"] = np.asarray(signals)
        elif signal_col in df.columns:
            df["signal"] = df[signal_col]
        else:
            raise ValueError(f"No signal array provided and '{signal_col}' not in DataFrame.")

        price = df["close"] if "close" in df.columns else df["price"]

        # Track state
        cash = self.initial_capital
        holdings = 0.0  # units of coin held
        current_pos = 0  # 0: flat, 1: long

        equity_history = []
        trades = []
        trades_pnl = []
        last_buy_price = 0.0

        for i in range(len(df)):
            p = float(price.iloc[i])
            sig = int(df["signal"].iloc[i])
            ts = df["timestamp"].iloc[i] if "timestamp" in df.columns else i

            # Strategy logic: long-only spot portfolio
            if sig == 2 and current_pos == 0:
                # Enter LONG
                effective_buy_price = p * (1.0 + self.slippage_rate)
                fee = cash * self.fee_rate
                investable = cash - fee
                holdings = investable / effective_buy_price
                cash = 0.0
                current_pos = 1
                last_buy_price = effective_buy_price
                trades.append({
                    "timestamp": ts,
                    "action": "BUY",
                    "price": p,
                    "exec_price": effective_buy_price,
                    "qty": holdings,
                    "fee": fee,
                })
            elif sig == 0 and current_pos == 1:
                # Exit to FLAT (SELL)
                effective_sell_price = p * (1.0 - self.slippage_rate)
                gross_proceeds = holdings * effective_sell_price
                fee = gross_proceeds * self.fee_rate
                cash = gross_proceeds - fee
                trade_pnl = (effective_sell_price - last_buy_price) / last_buy_price
                trades_pnl.append(trade_pnl)
                trades.append({
                    "timestamp": ts,
                    "action": "SELL",
                    "price": p,
                    "exec_price": effective_sell_price,
                    "qty": holdings,
                    "fee": fee,
                    "pnl_pct": trade_pnl,
                })
                holdings = 0.0
                current_pos = 0

            # Record current mark-to-market equity
            current_equity = cash + (holdings * p)
            equity_history.append(current_equity)

        df["equity"] = equity_history
        start_p = float(price.iloc[0])
        df["benchmark_equity"] = self.initial_capital * (price / start_p)
        df["strategy_bar_return"] = df["equity"].pct_change().fillna(0.0)

        if "timestamp" not in df.columns:
            df["timestamp"] = pd.date_range("2026-01-01", periods=len(df), freq="1s")

        # Performance analytics
        metrics = calculate_financial_metrics(
            equity_curve=df["equity"],
            benchmark_curve=df["benchmark_equity"],
            bar_returns=df["strategy_bar_return"],
            trades_pnl=trades_pnl,
        )

        output_cols = [c for c in ["timestamp", "price", "signal", "equity", "benchmark_equity"] if c in df.columns]

        return BacktestResult(
            metrics=metrics,
            equity_df=df[output_cols],
            trades=trades,
            initial_capital=self.initial_capital,
            final_capital=float(df["equity"].iloc[-1]),
        )
