"""Interactive Plotly visualizations for QuantPulse."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_price_and_volume(
    bars: pd.DataFrame,
    show_vwap: bool = True,
    show_bollinger: bool = True,
) -> go.Figure:
    """Create interactive Candlestick and Volume chart with indicator overlays."""
    b = bars.copy()
    has_ohlc = all(col in b.columns for col in ["open", "high", "low", "close"])

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25],
    )

    x_vals = b["timestamp"] if "timestamp" in b.columns else np.arange(len(b))

    if has_ohlc:
        fig.add_trace(
            go.Candlestick(
                x=x_vals,
                open=b["open"],
                high=b["high"],
                low=b["low"],
                close=b["close"],
                name="OHLC",
                increasing_line_color="#10B981",
                decreasing_line_color="#EF4444",
            ),
            row=1,
            col=1,
        )
    else:
        price = b["close"] if "close" in b.columns else b["price"]
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=price,
                mode="lines",
                name="Price",
                line=dict(color="#10B981", width=2),
                fill="tozeroy",
                fillcolor="rgba(16, 185, 129, 0.08)",
            ),
            row=1,
            col=1,
        )

    # Bollinger Bands overlay
    if show_bollinger and "bb_upper" in b.columns and "bb_lower" in b.columns:
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=b["bb_upper"],
                mode="lines",
                name="Upper BB",
                line=dict(color="#64748B", width=1, dash="dash"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=b["bb_lower"],
                mode="lines",
                name="Lower BB",
                line=dict(color="#64748B", width=1, dash="dash"),
                fill="tonexty",
                fillcolor="rgba(100, 116, 139, 0.05)",
            ),
            row=1,
            col=1,
        )

    # VWAP overlay
    if show_vwap and "vwap" in b.columns:
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=b["vwap"],
                mode="lines",
                name="VWAP",
                line=dict(color="#F59E0B", width=1.5),
            ),
            row=1,
            col=1,
        )

    # Volume Subplot
    vol = b["qty"] if "qty" in b.columns else b["quantity"]
    vol_colors = ["#10B981" if (b["close"].iloc[i] >= b["open"].iloc[i]) else "#EF4444" 
                  for i in range(len(b))] if has_ohlc else ["#38BDF8"] * len(b)

    fig.add_trace(
        go.Bar(
            x=x_vals,
            y=vol,
            name="Volume",
            marker_color=vol_colors,
            opacity=0.6,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1118",
        plot_bgcolor="#0E1620",
        margin=dict(l=10, r=40, t=10, b=10),
        height=420,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        font=dict(family="Plus Jakarta Sans", color="#94A3B8", size=11),
        yaxis=dict(side="right", gridcolor="#1B2836", tickprefix="$", tickformat=",.0f"),
        yaxis2=dict(side="right", gridcolor="#1B2836", showticklabels=False),
        xaxis2=dict(gridcolor="#1B2836"),
    )
    return fig


def plot_equity_curve(equity_df: pd.DataFrame) -> go.Figure:
    """Plot Strategy vs Benchmark equity curve."""
    df = equity_df.copy()
    x_vals = df["timestamp"] if "timestamp" in df.columns else np.arange(len(df))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=df["equity"],
            mode="lines",
            name="QuantPulse Strategy",
            line=dict(color="#10B981", width=2.5),
        )
    )
    if "benchmark_equity" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=df["benchmark_equity"],
                mode="lines",
                name="Buy & Hold Benchmark",
                line=dict(color="#64748B", width=1.5, dash="dot"),
            )
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1118",
        plot_bgcolor="#0E1620",
        margin=dict(l=10, r=40, t=20, b=20),
        height=320,
        hovermode="x unified",
        font=dict(family="Plus Jakarta Sans", color="#94A3B8", size=11),
        yaxis=dict(side="right", gridcolor="#1B2836", tickprefix="$", tickformat=",.0f"),
        xaxis=dict(gridcolor="#1B2836"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_oscillators(bars: pd.DataFrame) -> go.Figure:
    """Plot RSI and MACD subplots."""
    b = bars.copy()
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=["Relative Strength Index (RSI 14)", "MACD (12, 26, 9)"],
    )

    x_vals = b["timestamp"] if "timestamp" in b.columns else np.arange(len(b))

    # RSI
    if "rsi_14" in b.columns:
        fig.add_trace(
            go.Scatter(x=x_vals, y=b["rsi_14"], line=dict(color="#8B5CF6", width=2), name="RSI"),
            row=1,
            col=1,
        )
        fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", line_width=1, row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#10B981", line_width=1, row=1, col=1)

    # MACD
    if "macd_line" in b.columns and "macd_signal" in b.columns:
        fig.add_trace(
            go.Scatter(x=x_vals, y=b["macd_line"], line=dict(color="#38BDF8", width=1.5), name="MACD"),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(x=x_vals, y=b["macd_signal"], line=dict(color="#F59E0B", width=1.5), name="Signal"),
            row=2,
            col=1,
        )
        if "macd_hist" in b.columns:
            hist_colors = np.where(b["macd_hist"] >= 0, "#10B981", "#EF4444")
            fig.add_trace(
                go.Bar(x=x_vals, y=b["macd_hist"], marker_color=hist_colors, name="Hist"),
                row=2,
                col=1,
            )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1118",
        plot_bgcolor="#0E1620",
        margin=dict(l=10, r=40, t=30, b=10),
        height=320,
        showlegend=False,
        hovermode="x unified",
        font=dict(family="Plus Jakarta Sans", color="#94A3B8", size=10),
        yaxis=dict(side="right", gridcolor="#1B2836", range=[0, 100]),
        yaxis2=dict(side="right", gridcolor="#1B2836"),
        xaxis2=dict(gridcolor="#1B2836"),
    )
    return fig


def plot_confusion_matrix(cm_data: List[List[float]]) -> go.Figure:
    """Plot normalized Confusion Matrix heatmap."""
    labels = ["SELL", "HOLD", "BUY"]
    fig = go.Figure(
        data=go.Heatmap(
            z=cm_data,
            x=labels,
            y=labels,
            colorscale="Viridis",
            text=[[f"{val:.1%}" for val in row] for row in cm_data],
            texttemplate="%{text}",
            colorbar=dict(title="Rate"),
        )
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1118",
        plot_bgcolor="#0E1620",
        title="Multi-Class Confusion Matrix (Predicted vs Actual)",
        xaxis_title="Predicted Class",
        yaxis_title="True Class",
        height=280,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(family="Plus Jakarta Sans", color="#94A3B8", size=11),
    )
    return fig


def plot_feature_importance(importance_dict: Dict[str, float]) -> go.Figure:
    """Plot horizontal feature importance chart."""
    sorted_items = sorted(importance_dict.items(), key=lambda x: x[1])[-10:]
    names = [x[0] for x in sorted_items]
    vals = [x[1] for x in sorted_items]

    fig = go.Figure(
        go.Bar(
            x=vals,
            y=names,
            orientation="h",
            marker=dict(
                color=vals,
                colorscale="Teal",
            ),
        )
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1118",
        plot_bgcolor="#0E1620",
        title="Top Predictive Features",
        height=280,
        margin=dict(l=80, r=20, t=40, b=20),
        xaxis=dict(gridcolor="#1B2836"),
        yaxis=dict(gridcolor="#1B2836"),
        font=dict(family="Plus Jakarta Sans", color="#94A3B8", size=11),
    )
    return fig
