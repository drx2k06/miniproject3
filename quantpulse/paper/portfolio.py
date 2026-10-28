"""Stateful paper portfolio tracker with execution rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class PaperTradeRecord:
    """Historical execution record in paper trading ledger."""

    timestamp: str
    action: str  # BUY or SELL
    price: float
    quantity: float
    cost: float
    fee: float
    realized_pnl: float = 0.0


@dataclass
class PaperPortfolio:
    """Stateful simulated crypto portfolio."""

    initial_cash: float = 10000.0
    cash: float = 10000.0
    coin_qty: float = 0.0
    avg_entry_price: float = 0.0
    realized_pnl: float = 0.0
    fee_rate: float = 0.00075  # 0.075% taker fee
    trades: List[PaperTradeRecord] = field(default_factory=list)

    def total_value(self, current_price: float) -> float:
        """Calculate total mark-to-market portfolio value in USDT."""
        return self.cash + (self.coin_qty * current_price)

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized PnL in USDT."""
        if self.coin_qty <= 0:
            return 0.0
        return (current_price - self.avg_entry_price) * self.coin_qty

    def execute(
        self,
        action: str,
        price: float,
        risk_pct: float = 10.0,
        timestamp: Optional[str] = None,
    ) -> Optional[PaperTradeRecord]:
        """Execute simulated order and update portfolio state.

        Actions:
        - 'BUY': Spend risk_pct of available cash to purchase coin.
        - 'SELL': Sell all or proportional coins held.
        - 'HOLD': Do nothing.
        """
        now_str = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if action.upper() == "BUY":
            spend_amount = self.cash * (risk_pct / 100.0)
            if spend_amount <= 1.0:  # Minimum order threshold
                return None
            fee = spend_amount * self.fee_rate
            net_spend = spend_amount - fee
            bought_qty = net_spend / price

            # Update average entry price
            total_cost_basis = (self.avg_entry_price * self.coin_qty) + net_spend
            self.coin_qty += bought_qty
            self.avg_entry_price = total_cost_basis / self.coin_qty if self.coin_qty > 0 else 0.0
            self.cash -= spend_amount

            record = PaperTradeRecord(
                timestamp=now_str,
                action="BUY",
                price=price,
                quantity=bought_qty,
                cost=spend_amount,
                fee=fee,
                realized_pnl=0.0,
            )
            self.trades.append(record)
            return record

        elif action.upper() == "SELL" and self.coin_qty > 0:
            sold_qty = self.coin_qty
            gross_proceeds = sold_qty * price
            fee = gross_proceeds * self.fee_rate
            net_proceeds = gross_proceeds - fee

            cost_basis = sold_qty * self.avg_entry_price
            trade_pnl = net_proceeds - cost_basis
            self.realized_pnl += trade_pnl

            self.cash += net_proceeds
            self.coin_qty = 0.0
            self.avg_entry_price = 0.0

            record = PaperTradeRecord(
                timestamp=now_str,
                action="SELL",
                price=price,
                quantity=sold_qty,
                cost=gross_proceeds,
                fee=fee,
                realized_pnl=trade_pnl,
            )
            self.trades.append(record)
            return record

        return None


def paper_plan(
    signal: str,
    price: float,
    cash: float = 1000.0,
    risk_pct: float = 10.0,
) -> str:
    """Backward-compatible paper plan string generator."""
    spend = cash * risk_pct / 100.0
    if signal == "BUY":
        return f"Paper BUY: spend {spend:,.2f} USDT = {spend / price:.6f} coin (Risk: {risk_pct}%)"
    if signal == "SELL":
        return f"Paper SELL: exit coin position at ${price:,.2f}"
    return "HOLD: maintain cash / position equilibrium"
