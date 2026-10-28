"""QuantPulse - Institutional Cryptocurrency Analytics & Signal Dashboard.

Lead Developer: Daniel Richard Xavier
Conceptual Prototype Attribution: Divya-25-C (Stream Light)
"""
from __future__ import annotations

import io
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from app.styles import CUSTOM_CSS
from app.visualizer import (
    plot_confusion_matrix,
    plot_equity_curve,
    plot_feature_importance,
    plot_oscillators,
    plot_price_and_volume,
)
from quantpulse.backtest.engine import BacktestEngine
from quantpulse.config import default_config
from quantpulse.data.binance_client import BinanceClient
from quantpulse.data.csv_loader import TradeDataLoader
from quantpulse.data.synthetic import generate_synthetic_trades
from quantpulse.features.aggregator import to_bars
from quantpulse.features.pipeline import compute_features
from quantpulse.models.registry import get_models
from quantpulse.models.trainer import ModelTrainer
from quantpulse.paper.portfolio import PaperPortfolio, paper_plan
from quantpulse.security.validator import validate_csv_upload

# Configure Streamlit page layout
st.set_page_config(
    page_title="QuantPulse · Crypto Signal & Alpha Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom dark institutional theme
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initialize persistent session variables."""
    defaults = {
        "bars": None,
        "raw_trades": None,
        "data_source": "Synthetic Benchmark",
        "trained_models": None,
        "active_model_name": "Random Forest",
        "live_signal": None,
        "portfolio": PaperPortfolio(initial_cash=10000.0, cash=10000.0),
        "backtest_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()

# --------------------------------------------------------- SIDEBAR
with st.sidebar:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-icon">⚡</div>
            <div>
                <div class="brand-title">QuantPulse</div>
                <div class="brand-subtitle">Crypto Alpha & Signals</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Market Configuration")
    symbol = st.selectbox("Trading Pair", ["BTCUSDT", "ETHUSDT", "SOLUSDT"], index=0)
    bar_seconds = st.slider("Bar Interval (Seconds)", min_value=1, max_value=10, value=1)
    predict_ahead = st.slider("Prediction Horizon (Bars)", min_value=3, max_value=30, value=10)
    tail_share = st.slider("BUY / SELL Quantile Cutoff", min_value=15, max_value=35, value=25)

    st.markdown("---")
    st.markdown("### Data Source")
    data_mode = st.radio(
        "Source Mode",
        ["Synthetic Benchmark", "Binance Live REST", "Upload Custom CSV"],
        index=0,
    )

    if data_mode == "Upload Custom CSV":
        uploaded_file = st.file_uploader("Upload CSV Trades", type=["csv"])
        if uploaded_file is not None and st.button("Process Uploaded File", use_container_width=True):
            try:
                validate_csv_upload(uploaded_file)
                raw = TradeDataLoader.load(uploaded_file)
                bars = to_bars(raw, sec=bar_seconds)
                bars = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
                st.session_state.raw_trades = raw
                st.session_state.bars = bars
                st.session_state.data_source = uploaded_file.name
                st.session_state.trained_models = None
                st.success(f"Loaded {len(bars):,} bars from {uploaded_file.name}")
            except Exception as e:
                st.error(f"Upload error: {e}")

    elif data_mode == "Binance Live REST":
        if st.button("Fetch Live Binance Trades", use_container_width=True):
            with st.spinner("Connecting to Binance Vision REST endpoint..."):
                try:
                    client = BinanceClient(base_url=default_config.binance_base_url)
                    raw = client.fetch_trades(symbol=symbol, limit=1000)
                    bars = to_bars(raw, sec=bar_seconds)
                    bars = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
                    if len(bars) < 20:
                        st.warning("Low trade density on 1s bars. Synthesizing context buffer...")
                        synth = generate_synthetic_trades(n_trades=3000)
                        raw = synth
                        bars = to_bars(synth, sec=bar_seconds)
                        bars = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
                    st.session_state.raw_trades = raw
                    st.session_state.bars = bars
                    st.session_state.data_source = f"Binance Vision ({symbol})"
                    st.session_state.trained_models = None
                    st.success(f"Fetched {len(bars):,} live bars")
                except Exception as e:
                    st.error(f"Live fetch failed: {e}")

    elif data_mode == "Synthetic Benchmark":
        if st.session_state.bars is None or st.session_state.data_source != "Synthetic Benchmark":
            synth = generate_synthetic_trades(n_trades=25000, seed=42)
            bars = to_bars(synth, sec=bar_seconds)
            bars = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
            st.session_state.raw_trades = synth
            st.session_state.bars = bars
            st.session_state.data_source = "Synthetic Benchmark"

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:11px; color:#64748B; line-height:1.6;">
            <b>QuantPulse 2.0</b><br>
            Developed by Daniel Richard Xavier<br>
            Educational & Quantitative Research Only.<br>
            No real orders are routed to live exchanges.
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------- DATA PREP
bars = st.session_state.bars
if bars is None or bars.empty:
    synth = generate_synthetic_trades(n_trades=25000, seed=42)
    bars = to_bars(synth, sec=1)
    bars = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
    st.session_state.bars = bars
    st.session_state.raw_trades = synth

current_price = float(bars["close"].iloc[-1]) if "close" in bars.columns else float(bars["price"].iloc[-1])
portfolio = st.session_state.portfolio
port_value = portfolio.total_value(current_price)
unrealized = portfolio.unrealized_pnl(current_price)

# --------------------------------------------------------- HEADER METRICS
h1, h2, h3, h4, h5 = st.columns(5)
with h1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Market Price</div>
            <div class="metric-value">${current_price:,.2f}</div>
            <div class="metric-sub">{symbol} · {st.session_state.data_source}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Bars Analyzed</div>
            <div class="metric-value">{len(bars):,}</div>
            <div class="metric-sub">{bar_seconds}s Aggregated Bars</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active Model</div>
            <div class="metric-value" style="font-size:20px;">{st.session_state.active_model_name}</div>
            <div class="metric-sub">Walk-Forward Horizon: {predict_ahead}b</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Paper Portfolio</div>
            <div class="metric-value">${port_value:,.2f}</div>
            <div class="metric-sub">Cash: ${portfolio.cash:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h5:
    badge_color = "pill-green" if unrealized >= 0 else "pill-red"
    pnl_sign = "+" if unrealized >= 0 else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Unrealized PnL</div>
            <div class="metric-value" style="color: {'#10B981' if unrealized >= 0 else '#EF4444'};">
                {pnl_sign}${unrealized:,.2f}
            </div>
            <div class="metric-sub">Coins: {portfolio.coin_qty:.5f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# --------------------------------------------------------- TABS
tabs = st.tabs([
    "📊 Live Market & Signals",
    "📈 Oscillators & Flow",
    "🧠 Model Training & CV",
    "⚡ Strategy Backtesting",
    "💼 Paper Portfolio",
    "🔬 Synthetic Studio",
    "📖 Documentation & Architecture",
])

# --------------------------------------------------------- TAB 1: LIVE SIGNALS
with tabs[0]:
    c_chart, c_signal = st.columns([1.8, 1.0], gap="large")

    with c_chart:
        st.markdown(
            """
            <div class="panel-box">
                <div class="panel-title">Price Action & Microstructure Volume</div>
                <div class="panel-caption">High-frequency Candlesticks with Bollinger Bands and VWAP overlays</div>
            """,
            unsafe_allow_html=True,
        )
        fig_price = plot_price_and_volume(bars.tail(300), show_vwap=True, show_bollinger=True)
        st.plotly_chart(fig_price, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c_signal:
        sig_data = st.session_state.live_signal
        if sig_data is None:
            sig_name = "HOLD"
            conf = 0.50
            sig_price = current_price
            pill_class = "pill-amber"
        else:
            sig_name, conf, sig_price = sig_data
            pill_class = "pill-green" if sig_name == "BUY" else ("pill-red" if sig_name == "SELL" else "pill-amber")

        st.markdown(
            f"""
            <div class="signal-hero">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#94A3B8; font-weight:700;">
                        Latest Quantitative Signal
                    </div>
                    <span class="signal-status-pill {pill_class}">● {sig_name}</span>
                </div>
                <div style="font-size:42px; font-weight:800; letter-spacing:-1px; margin: 12px 0 4px; color:{'#10B981' if sig_name=='BUY' else ('#EF4444' if sig_name=='SELL' else '#F59E0B')};">
                    {sig_name}
                </div>
                <div style="font-size:13px; color:#CBD5E1; margin-bottom:12px;">
                    Confidence: <b>{conf:.1%}</b> &nbsp;·&nbsp; Price: <b>${sig_price:,.2f}</b>
                </div>
                <div style="background:#1E293B; height:6px; border-radius:3px; overflow:hidden;">
                    <div style="width:{conf:.1%}; height:100%; background:#10B981; border-radius:3px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        current_plan = paper_plan(sig_name, sig_price, cash=portfolio.cash, risk_pct=10.0)
        st.info(f"**Execution Plan:** {current_plan}")

        available_models = list(get_models().keys())
        selected_model_name = st.selectbox(
            "Select Inference Model",
            available_models,
            index=0,
            key="model_select_box",
        )
        st.session_state.active_model_name = selected_model_name

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Poll Live Signal", use_container_width=True):
                if st.session_state.trained_models is None or selected_model_name not in st.session_state.trained_models:
                    st.warning("Training selected model first...")
                    models = get_models()
                    m = models[selected_model_name]
                    res = ModelTrainer.train(bars, m, ahead=predict_ahead, tail=tail_share / 100.0)
                    if st.session_state.trained_models is None:
                        st.session_state.trained_models = {}
                    st.session_state.trained_models[selected_model_name] = res

                m_res = st.session_state.trained_models[selected_model_name]
                last_row = bars.iloc[[-1]]
                feats = m_res.feature_names
                p = m_res.model.predict_proba(last_row[feats])[0]
                cls_idx = int(m_res.model.classes_[p.argmax()])
                sig_name = default_config.label_names.get(cls_idx, "HOLD")
                conf = float(p.max())
                st.session_state.live_signal = (sig_name, conf, current_price)
                st.rerun()

        with col_b2:
            if st.button("Execute Paper Order", use_container_width=True):
                rec = portfolio.execute(sig_name, current_price, risk_pct=10.0)
                if rec:
                    st.success(f"Executed Paper {rec.action} at ${rec.price:,.2f}")
                else:
                    st.info("No order executed (HOLD signal or zero balance).")
                st.rerun()

# --------------------------------------------------------- TAB 2: OSCILLATORS
with tabs[1]:
    st.markdown(
        """
        <div class="panel-box">
            <div class="panel-title">Microstructure Order Flow & Technical Indicators</div>
            <div class="panel-caption">Real-time RSI, MACD Histogram, and Order Flow Imbalance Dynamics</div>
        """,
        unsafe_allow_html=True,
    )
    fig_osc = plot_oscillators(bars.tail(300))
    st.plotly_chart(fig_osc, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------- TAB 3: MODEL TRAINING & CV
with tabs[2]:
    st.markdown(
        """
        <div class="panel-box">
            <div class="panel-title">Supervised Machine Learning & Walk-Forward Cross-Validation</div>
            <div class="panel-caption">Train tree-based and linear classifiers on forward quantile returns</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚀 Train & Evaluate All Models", use_container_width=True):
        models = get_models()
        results = {}
        progress = st.progress(0, text="Training models...")
        for i, (name, m) in enumerate(models.items(), start=1):
            res = ModelTrainer.train(bars, m, ahead=predict_ahead, tail=tail_share / 100.0, test_ratio=0.30)
            results[name] = res
            progress.progress(i / len(models), text=f"Trained {name}")
        st.session_state.trained_models = results
        st.rerun()

    if st.session_state.trained_models:
        rows = []
        for name, res in st.session_state.trained_models.items():
            edge = res.accuracy - res.baseline
            rows.append({
                "Model": name,
                "Accuracy": f"{res.accuracy:.3f}",
                "Baseline (Majority)": f"{res.baseline:.3f}",
                "Balanced Accuracy": f"{res.metrics['balanced_accuracy']:.3f}",
                "Macro F1": f"{res.metrics['f1_macro']:.3f}",
                "Edge vs Baseline": f"{edge:+.3f}",
                "Status": "✅ Outperforming" if edge > 0 else "⚠️ Sub-Baseline",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        col_cm, col_fi = st.columns(2)
        active_res = st.session_state.trained_models.get(
            st.session_state.active_model_name,
            list(st.session_state.trained_models.values())[0],
        )

        with col_cm:
            st.plotly_chart(
                plot_confusion_matrix(active_res.metrics["confusion_matrix_norm"]),
                use_container_width=True,
            )

        with col_fi:
            if active_res.feature_importance:
                st.plotly_chart(
                    plot_feature_importance(active_res.feature_importance),
                    use_container_width=True,
                )
    else:
        st.info("Click 'Train & Evaluate All Models' to run walk-forward training across the dataset.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------- TAB 4: BACKTESTING STUDIO
with tabs[3]:
    st.markdown(
        """
        <div class="panel-box">
            <div class="panel-title">Quantitative Strategy Backtesting Engine</div>
            <div class="panel-caption">Simulate model signals under realistic exchange frictions (maker/taker fees & slippage)</div>
        """,
        unsafe_allow_html=True,
    )

    bt_c1, bt_c2, bt_c3 = st.columns(3)
    with bt_c1:
        taker_fee_bps = st.number_input("Taker Fee (Basis Points)", min_value=0.0, max_value=50.0, value=7.5)
    with bt_c2:
        slippage_bps = st.number_input("Execution Slippage (bps)", min_value=0.0, max_value=50.0, value=5.0)
    with bt_c3:
        initial_cap = st.number_input("Initial Capital (USDT)", min_value=100.0, value=10000.0, step=1000.0)

    if st.button("Run Historical Backtest", use_container_width=True):
        if st.session_state.trained_models is None or st.session_state.active_model_name not in st.session_state.trained_models:
            st.info("Training active model to generate out-of-sample predictions...")
            models = get_models()
            m = models[st.session_state.active_model_name]
            res = ModelTrainer.train(bars, m, ahead=predict_ahead, tail=tail_share / 100.0)
            if st.session_state.trained_models is None:
                st.session_state.trained_models = {}
            st.session_state.trained_models[st.session_state.active_model_name] = res

        m_res = st.session_state.trained_models[st.session_state.active_model_name]
        engine = BacktestEngine(
            fee_rate=taker_fee_bps / 10000.0,
            slippage_rate=slippage_bps / 10000.0,
            initial_capital=initial_cap,
        )
        bt_res = engine.run(m_res.test_data, signal_col="prediction")
        st.session_state.backtest_result = bt_res

    bt_res = st.session_state.backtest_result
    if bt_res is not None:
        m = bt_res.metrics
        st.plotly_chart(plot_equity_curve(bt_res.equity_df), use_container_width=True)

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Strategy Return", f"{m['strategy_return']:+.2%}")
        k2.metric("Benchmark Return", f"{m['benchmark_return']:+.2%}")
        k3.metric("Excess Alpha", f"{m['alpha']:+.2%}")
        k4.metric("Sharpe Ratio", f"{m['sharpe_ratio']:.2f}")
        k5.metric("Sortino Ratio", f"{m['sortino_ratio']:.2f}")
        k6.metric("Max Drawdown", f"{m['max_drawdown']:.2%}")

        if bt_res.trades:
            st.markdown("#### Recent Simulated Executions")
            st.dataframe(pd.DataFrame(bt_res.trades).tail(10), hide_index=True, use_container_width=True)
    else:
        st.caption("Click 'Run Historical Backtest' to simulate performance.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------- TAB 5: PAPER PORTFOLIO
with tabs[4]:
    st.markdown(
        """
        <div class="panel-box">
            <div class="panel-title">Stateful Paper Trading Ledger</div>
            <div class="panel-caption">Real-time simulated account balance, crypto holdings, and fill history</div>
        """,
        unsafe_allow_html=True,
    )

    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        st.markdown(
            f"""
            <div class="metric-card" style="margin-bottom:12px;">
                <div class="metric-label">Available USDT Cash</div>
                <div class="metric-value">${portfolio.cash:,.2f}</div>
            </div>
            <div class="metric-card" style="margin-bottom:12px;">
                <div class="metric-label">Coin Holdings ({symbol})</div>
                <div class="metric-value">{portfolio.coin_qty:.6f}</div>
                <div class="metric-sub">Avg Entry: ${portfolio.avg_entry_price:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Realized Net PnL</div>
                <div class="metric-value" style="color:{'#10B981' if portfolio.realized_pnl >= 0 else '#EF4444'};">
                    {'+' if portfolio.realized_pnl >= 0 else ''}${portfolio.realized_pnl:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_col2:
        if portfolio.trades:
            trade_rows = [
                {
                    "Time": t.timestamp,
                    "Action": t.action,
                    "Price": f"${t.price:,.2f}",
                    "Quantity": f"{t.quantity:.6f}",
                    "Cost/Proceeds": f"${t.cost:,.2f}",
                    "Fee": f"${t.fee:,.4f}",
                    "Realized PnL": f"${t.realized_pnl:,.2f}",
                }
                for t in portfolio.trades
            ]
            st.dataframe(pd.DataFrame(trade_rows).iloc[::-1], hide_index=True, use_container_width=True)
        else:
            st.info("No paper executions recorded yet. Execute an order from the 'Live Market & Signals' tab.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------- TAB 6: SYNTHETIC STUDIO
with tabs[5]:
    st.markdown(
        """
        <div class="panel-box">
            <div class="panel-title">Merton Jump-Diffusion Synthetic Market Studio</div>
            <div class="panel-caption">Generate high-frequency trade order flow with clustered Hawkes arrivals for offline testing</div>
        """,
        unsafe_allow_html=True,
    )

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        synth_n = st.number_input("Number of Trades", min_value=1000, max_value=100000, value=30000, step=5000)
    with sc2:
        synth_vol = st.slider("Diffusive Volatility (sigma)", min_value=0.0005, max_value=0.0050, value=0.0015, step=0.0001, format="%.4f")
    with sc3:
        synth_jumps = st.slider("Jump Arrival Intensity", min_value=0.0, max_value=0.10, value=0.02, step=0.01)

    if st.button("Generate Fresh Synthetic Dataset", use_container_width=True):
        from quantpulse.data.synthetic import SyntheticMarketGenerator
        gen = SyntheticMarketGenerator(volatility=synth_vol, jump_intensity=synth_jumps)
        fresh_trades = gen.generate(n_trades=synth_n)
        fresh_bars = to_bars(fresh_trades, sec=bar_seconds)
        fresh_bars = compute_features(fresh_bars, mode="full").dropna(subset=default_config.baseline_features)
        st.session_state.raw_trades = fresh_trades
        st.session_state.bars = fresh_bars
        st.session_state.data_source = "Synthetic Benchmark (Custom)"
        st.session_state.trained_models = None
        st.session_state.backtest_result = None
        st.success(f"Generated {len(fresh_bars):,} feature bars from {len(fresh_trades):,} synthetic trades!")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------- TAB 7: DOCS
with tabs[6]:
    st.markdown(
        """
        <div class="panel-box">
            <div class="panel-title">QuantPulse Technical Architecture & Attribution</div>
            <div class="panel-caption">System specifications, mathematics, and open-source credits</div>
            <div style="font-size:13px; color:#CBD5E1; line-height:1.7;">
                <h4>Lead Developer & Architect</h4>
                <p><b>Daniel Richard Xavier</b> — Re-engineered architecture, walk-forward cross validation, 
                transaction cost backtesting simulator, stateful paper portfolio ledger, and Streamlit workstation.</p>
                
                <h4>Original Conceptual Prototype Attribution</h4>
                <p><b>Divya-25-C</b> (<a href="https://github.com/Divya-25-C/crypto_project.git" target="_blank" style="color:#10B981;">crypto_project</a>) — 
                Original concept for supervised trade flow classification on Binance tick data.</p>
                
                <h4>Mathematical Foundations</h4>
                <ul>
                    <li><b>Order Flow Imbalance (OFI):</b> <code>flow = (2 * Buy_Vol / Total_Vol) - 1</code> bounded in [-1.0, 1.0].</li>
                    <li><b>Merton Jump-Diffusion:</b> Geometric Brownian Motion with compound Poisson jump arrivals for realistic flash crashes and spikes.</li>
                    <li><b>Walk-Forward Cross Validation:</b> Strict temporal separation with zero lookahead bias or future data leakage.</li>
                    <li><b>Trading Frictions:</b> 7.5 bps taker commission + 5.0 bps execution slippage applied to all simulated rebalances.</li>
                </ul>
                
                <h4>Financial Disclaimer</h4>
                <p><i>QuantPulse is an educational and quantitative research framework. Cryptocurrency markets are highly volatile. 
                Past simulated backtest results do not guarantee future performance. No actual orders are placed on real exchanges.</i></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
