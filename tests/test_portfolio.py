"""Tests for stateful paper trading portfolio simulator."""
import pytest

from quantpulse.paper.portfolio import PaperPortfolio, paper_plan


def test_paper_portfolio_lifecycle():
    port = PaperPortfolio(initial_cash=10000.0, cash=10000.0)

    # Initial state
    assert port.cash == 10000.0
    assert port.coin_qty == 0.0
    assert port.realized_pnl == 0.0
    assert port.total_value(current_price=50000.0) == 10000.0

    # Execute BUY (10% risk -> $1,000)
    rec1 = port.execute(action="BUY", price=50000.0, risk_pct=10.0)
    assert rec1 is not None
    assert rec1.action == "BUY"
    assert port.cash < 10000.0
    assert port.coin_qty > 0.0
    assert port.avg_entry_price > 0.0

    # Unrealized PnL when price rises to 60,000
    unrealized = port.unrealized_pnl(current_price=60000.0)
    assert unrealized > 0.0
    assert port.total_value(current_price=60000.0) > 10000.0

    # Execute SELL at 60,000
    rec2 = port.execute(action="SELL", price=60000.0)
    assert rec2 is not None
    assert rec2.action == "SELL"
    assert port.coin_qty == 0.0
    assert port.realized_pnl > 0.0
    assert port.cash > 10000.0
    assert len(port.trades) == 2


def test_paper_plan_strings():
    p_buy = paper_plan("BUY", 65000.0, cash=1000.0, risk_pct=10)
    p_sell = paper_plan("SELL", 65000.0)
    p_hold = paper_plan("HOLD", 65000.0)

    assert "Paper BUY" in p_buy
    assert "Paper SELL" in p_sell
    assert "HOLD" in p_hold
