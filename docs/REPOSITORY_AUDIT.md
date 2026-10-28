# Quantitative & Architecture Audit Report: Stream Light (Reference Repository)

**Audited Repository:** `https://github.com/Divya-25-C/crypto_project.git`  
**Reference Commit:** `b3809d3ad2e8f748449f9c145a4f7bb9525768c9`  
**Author:** Divya-25-C  
**Audit Conducted By:** Daniel Richard Xavier (Senior Quantitative Systems Engineer & Software Architect)  
**Date:** October 2026  
**Environment:** Windows 10/11, Python 3.12, Git, Streamlit  

---

## 1. Executive Summary

The reference repository `crypto_project` provides an educational prototype named **"Stream Light"**, designed to demonstrate supervised machine learning for cryptocurrency direction classification (BUY / HOLD / SELL) based on Binance trade order flow, accompanied by a Streamlit interactive dashboard and an HTML preview.

While the conceptual idea of deriving microstructure order-flow imbalance from trade ticks is solid, the reference codebase suffers from critical architectural bottlenecks, quantitative flaws, absence of backtesting and portfolio state, complete lack of automated testing, and severe usability constraints. Most notably, the trained models perform **below the trivial majority-class baseline** (~37-39% accuracy vs 61.1% baseline), paper trading is merely static string interpolation without capital tracking or fee deduction, and live signal polling breaks under normal market volatility due to restrictive 1,000-trade query limits.

This audit details the structural, quantitative, financial, security, and UI/UX findings to establish the baseline for re-engineering **QuantPulse / AegisCrypto**, an institutional-grade crypto signal, backtesting, and portfolio simulation platform.

---

## 2. Repository Inventory & Baseline Metrics

### 2.1 File Structure & Manifest
The reference repository contains exactly 5 files with 407 lines of code:

| File | Lines | Primary Responsibility | Critical Findings |
|---|---|---|---|
| `crypto.py` | 136 | Data loading, bar aggregation, feature calculation, model training, live polling, paper plan | Monolithic; global state; 0 unit tests; models underperform trivial baseline. |
| `app.py` | 237 | Streamlit web interface | Tightly coupled with `crypto.py`; synthetic fallback data; hardcoded sample metrics. |
| `preview.html` | 21 | Standalone HTML/CSS mockup | Hardcoded static visualization; simulated DOM toast handlers. |
| `requirements.txt` | 8 | Python dependencies | Unpinned packages (`pandas`, `numpy`, `scikit-learn`, `xgboost`, `requests`, `python-dotenv`, `streamlit>=1.36`, `plotly`). |
| `.gitignore` | 5 | Git exclusion rules | Excludes `.env`, `__pycache__/`, `*.csv`, `crypto project/`. |

- **License:** None declared.
- **Git Commit History:** Single initial commit (`b3809d3ad2e8f748449f9c145a4f7bb9525768c9`).
- **Test Suite:** Non-existent (0% test coverage).
- **Documentation:** Non-existent (no root `README.md`, no architecture documentation, no setup guides).

---

## 3. Quantitative & Machine Learning Defects

### 3.1 Sub-Baseline Model Performance
The reference implementation trains `DecisionTreeClassifier` (depth 5) and `RandomForestClassifier` (200 trees, depth 5) to predict price return direction over `ahead=10` future bars. 

- **Empirical Baseline:** With quantile cutoffs `tail=0.25`, the middle class (HOLD) comprises approximately 50% of the training distribution. However, on test splits, class imbalance frequently skews the majority class to 60–65%.
- **Reported Test Accuracy:**
  - Decision Tree: **0.376** (Baseline: **0.611**) $\rightarrow$ **-23.5% below baseline**
  - Random Forest: **0.389** (Baseline: **0.611**) $\rightarrow$ **-22.2% below baseline**
- **Root Cause:** 
  1. Low signal-to-noise ratio in 1-second raw tick bars.
  2. Sparse feature space (only 6 features: `ret_1`, `ret_5`, `vol_20`, `flow`, `flow_5`, `log_qty`).
  3. Strict tree depth limitation (`max_depth=5`) combined with noisy short-horizon returns.
  4. Absence of feature normalization, momentum indicators, or regime indicators.

### 3.2 Evaluation Metrics Deficiency
- The system computes only raw scalar accuracy: `(model.predict(te[FEATS]) == label(te)).mean()`.
- Multi-class classification with imbalanced labels requires:
  - Class-specific Precision, Recall, and F1-Score.
  - Balanced Accuracy.
  - Macro and Weighted F1-Scores.
  - Confusion Matrix analysis (to assess dangerous false-positive BUY/SELL errors).
  - Probability calibration and ROC-AUC curves.

### 3.3 Data Leakage & Cross-Validation Risks
- The reference implementation utilizes a single static chronological split (`cut = int(len(d) * (1 - test))`).
- While chronological splitting avoids simple forward look-ahead bias, it provides zero insight into model stability across different market volatility regimes (bullish trend, flash crash, range-bound consolidation).
- Lack of Purged Time-Series Cross-Validation / Walk-Forward Cross-Validation results in overfitting to specific time windows.

---

## 4. Financial & Algorithmic Deficiencies

### 4.1 Illusion of Paper Trading
In `crypto.py`:
```python
def paper_plan(signal, price, cash=1000.0, risk_pct=10):
    spend = cash * risk_pct / 100
    if signal == "BUY":
        return f"Paper BUY: spend {spend:,.2f} USDT = {spend / price:.6f} coin"
    if signal == "SELL":
        return "Paper SELL: sell part of the coin you hold"
    return "HOLD: do nothing"
```
- **Finding:** This is not a paper trading engine. It is a static text formatter.
- **Missing Elements:**
  - No persistent portfolio state (cash balance, inventory, average entry price).
  - No trade execution ledger or historical fill records.
  - Zero consideration of exchange transaction fees (Binance charges 0.075% - 0.10% per trade; high-frequency rebalancing wipes out thin alpha).
  - Zero slippage modeling or liquidity depth verification.
  - No position sizing logic (fixed Kelly criterion or volatility-adjusted sizing).
  - No Stop-Loss, Take-Profit, or Trailing-Stop risk parameters.

### 4.2 Complete Absence of Backtesting
- A crypto signal engine must demonstrate historical viability before deployment.
- The reference system provides no historical simulation capability to calculate Sharpe ratio, Sortino ratio, Maximum Drawdown, or cumulative Equity Curve.

---

## 5. Architectural & Software Engineering Defects

### 5.1 Global Mutable State & Tight Coupling
- `crypto.py` exposes module-level constants `BASE`, `SYMBOL`, `DATA_FILE`, `NAMES`, `FEATS` that cannot be dynamically overridden without altering module internals.
- No class encapsulation or object-oriented design patterns. Data processing, model training, live polling, and business logic are packed into loose functions.

### 5.2 Fragile Live API Integration
```python
def live_signal(model, sec=1):
    r = requests.get(f"{BASE}/api/v3/trades", params={"symbol": SYMBOL, "limit": 1000}, timeout=10)
    r.raise_for_status()
    ...
    live = features(to_bars(d, sec)).dropna(subset=FEATS)
    last = live.iloc[[-1]]
```
- **Critical Flaw:** The Binance public endpoint `/api/v3/trades` returns a maximum limit of 1,000 trades.
- For high-volume pairs like BTC/USDT, 1,000 trades can span merely 8 to 25 seconds of activity.
- Grouping 1,000 trades into 1-second bars yields only 8–25 rows.
- The feature calculation `vol_20 = b["ret_1"].rolling(20).std()` requires at least 20 bars to compute without producing `NaN`.
- Consequently, `dropna(subset=FEATS)` frequently drops all rows or yields an empty DataFrame, causing `IndexError: single positional indexer is out-of-bounds` on `last = live.iloc[[-1]]`.

### 5.3 Lack of Input Validation & Data Robustness
- In `load_trades(file, nrows=None)`, the function checks `str(head.iloc[0, 0]).isdigit()` to infer header existence. If a user uploads an empty CSV, a malformed CSV, or a dataset with custom columns, the application crashes without informative error feedback.
- Date parsing uses brittle thresholding: `unit = "us" if d["time"].max() > 1e14 else "ms"`.

---

## 6. Security & Operational Review

| Checkpoint | Status | Finding & Recommendation |
|---|---|---|
| **Hardcoded Secrets** | Clean | No live API keys, seed phrases, or credentials found in source files. |
| **Secret Management** | Adequate | `.env` is listed in `.gitignore`. However, no `.env.example` template is provided for developers. |
| **Rate Limiting & DoS** | High Risk | Unthrottled calls to `requests.get` without exponential backoff or circuit breaking. |
| **Financial Claims** | Low Risk | UI clearly states "Paper money only · Signals are educational examples, not financial advice". |
| **Input Sanitization** | Missing | Uploaded file bytes are processed directly without MIME-type or payload size guardrails. |

---

## 7. UI/UX Assessment

1. **Synthetic Data Disconnection:** When no CSV is uploaded, `app.py` falls back to `sample_data()` which generates an idealized sine-wave price series. However, model training is disabled while sample data is active, leaving new users stuck unless they independently acquire a 500MB Binance raw trades file.
2. **Missing Real-Time Continuous Streaming:** The dashboard relies on manual button clicks for "Get live signal", lacking automated polling, auto-refresh intervals, or WebSockets.
3. **Limited Visualizations:** The interface only provides a single 2D line plot of price. Traders require Candlestick (OHLCV) charts, Volume profiles, Technical Indicator overlays (RSI, Bollinger Bands, VWAP), Order-Flow Imbalance heatmaps, and Confusion Matrices.

---

## 8. Summary of Re-Engineering Objectives

To transform this academic prototype into an institutional-grade crypto analytics system, our re-engineered platform (**QuantPulse Crypto Engine**) must achieve:

1. **Modular Architecture:** Clean separation into `engine/data`, `engine/features`, `engine/models`, `engine/backtest`, `engine/paper`, `engine/security`, and `app/`.
2. **Expanded Alpha Feature Suite:** Moving from 6 basic features to 20+ robust microstructure and technical indicators (RSI, MACD, Bollinger Bands, VWAP, Order Flow Imbalance, Realized Volatility, Momentum).
3. **Walk-Forward ML Pipeline:** Purged cross-validation, hyperparameter tuning, model ensemble (Random Forest, Gradient Boosting, LightGBM, Logistic Regression), and comprehensive multi-class metrics (Balanced Accuracy, F1, ROC-AUC, Confusion Matrix).
4. **Authentic Backtesting Simulator:** Full historical simulation engine with maker/taker fee accounting (0.075%), slippage penalties, equity curve, Sharpe/Sortino ratios, and maximum drawdown analytics.
5. **Stateful Paper Trading Engine:** Real-time simulated execution ledger tracking cash, crypto inventory, average cost basis, realized/unrealized PnL, and Stop-Loss / Take-Profit triggers.
6. **Robust Data Fallbacks:** Integrated Binance REST API client with intelligent trade window stitching, plus a realistic synthetic Microstructure Jump-Diffusion Generator for instant offline testing and demonstration.
7. **Production Test Suite:** 100% unit and integration test coverage across all mathematical models, feature extractors, and backtesting pipelines.
8. **Enterprise Documentation:** Full setup guides, evaluation reports, mathematical formulations, and verified Windows run instructions.
