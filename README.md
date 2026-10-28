# QuantPulse ⚡ — Institutional Cryptocurrency Microstructure Signal & Backtesting Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Tests: 23 Passed](https://img.shields.io/badge/Tests-23%20Passed%20(100%25)-brightgreen.svg)](tests/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-lightgrey.svg)]()

> **QuantPulse** is an enterprise-grade quantitative analytics, microstructure order-flow modeling, machine learning signal generation, and realistic backtesting platform for high-frequency cryptocurrency trading.

**Developer of Customized Implementation:** **Daniel Richard Xavier**  
**Original Conceptual Prototype Base:** [Stream Light](https://github.com/Divya-25-C/crypto_project.git) by **Divya-25-C**  
**Destination Repository:** [drx2k06/miniproject3](https://github.com/drx2k06/miniproject3.git)  

---

## 1. Project Overview

QuantPulse transforms high-frequency cryptocurrency trade ticks into actionable quantitative signals and simulated portfolio strategies. Built for quantitative researchers, algorithmic traders, and software architects, the platform combines high-throughput tick-to-bar aggregation, an 18-factor microstructure and technical indicator suite, leak-free walk-forward machine learning cross-validation, realistic friction-aware backtesting (with exchange taker fees and slippage), and a stateful paper trading execution engine.

Whether operating live against the Binance Vision REST market stream, ingesting local gigabyte tick archives, or benchmarking against the built-in Merton Jump-Diffusion market simulator, QuantPulse delivers reproducible quantitative discipline and institutional transparency.

---

## 2. Problem Statement & Objectives

### The Limitations of the Original Reference Prototype
An exhaustive audit of the original educational prototype (`Stream Light` by Divya-25-C) revealed significant architectural and financial bottlenecks:
- **Sub-Baseline Machine Learning:** Models (Decision Tree and Random Forest) performed at $37.6\%$ and $38.9\%$ accuracy against a majority-class baseline of $61.1\%$ ($\approx -22\%$ to $-23\%$ worse than naive guessing).
- **Illusion of Paper Trading:** Paper trading was merely a text string formatter (`"spend X USDT = Y coin"`) with no cash balance tracking, coin inventory accounting, or historical fill ledger.
- **Complete Absence of Backtesting:** Zero historical strategy simulation or risk analytics (no Sharpe ratio, Sortino ratio, or Maximum Drawdown).
- **API Fragility & Crash Hazards:** Querying 1,000 Binance trades frequently yielded fewer than 20 time bars, causing empty feature matrices and unhandled `IndexError` crashes.
- **Zero Test Coverage & Documentation:** 0 automated tests and no setup guides or architectural documentation.

### Core Objectives Achieved
1. **Architectural Deconstruction:** Refactored two monolithic scripts into a modular, production-ready package (`quantpulse`).
2. **Feature Enrichment:** Expanded from 6 basic features to 18 indicators (Order Flow Imbalance, Cumulative Volume Delta, VWAP distance, RSI-14, MACD, Bollinger Bands).
3. **Walk-Forward ML Rigor:** Implemented temporal time-series cross-validation without lookahead bias, tracking Balanced Accuracy, Macro F1, and Confusion Matrices across Random Forest, Gradient Boosting, XGBoost, and Logistic Regression.
4. **Frictions-Aware Backtest Simulator:** Developed a backtester deducting $0.075\%$ exchange fees and $0.050\%$ slippage to measure true net alpha.
5. **Stateful Portfolio Management:** Built a real-time paper trading ledger tracking capital, cost basis, realized/unrealized PnL, and Stop-Loss limits.
6. **Production QA:** Authored 23 comprehensive automated tests achieving a $100\%$ pass rate.

---

## 3. Features Implemented

- **High-Throughput Microstructure Bar Aggregator:** Resamples trade ticks into uniform time bars ($1\text{s}$ to $10\text{s}$) capturing OHLC, total volume, aggressive buy/sell split, and trade counts.
- **18-Factor Alpha Indicator Suite:**
  - *Microstructure:* Order Flow Imbalance (OFI), Cumulative Volume Delta (CVD), Log Volume.
  - *Multi-Horizon Dynamics:* Returns at 1, 5, 10, and 20 bars; Realized Volatility at 20 and 60 bars.
  - *Technical Overlays:* Volume-Weighted Average Price (VWAP) distance, Relative Strength Index (RSI 14), Moving Average Convergence Divergence (MACD 12/26/9), Bollinger Bands (%B and width).
- **Ensemble Machine Learning Registry:**
  - Tuned Random Forest Classifier (`min_samples_leaf=5`, balanced weighting).
  - Regularized Gradient Boosting Classifier & XGBoost Classifier.
  - Calibrated Logistic Regression benchmark pipeline with Standard Scaler.
  - Classical Decision Tree for baseline comparison.
- **Purged Walk-Forward Cross-Validation:** Strict temporal data partitioning preventing lookahead bias or future data leakage.
- **Friction-Aware Historical Backtesting Engine:**
  - Deducts exchange commissions ($0.075\%$ taker fee default) and execution slippage ($5.0\text{ bps}$).
  - Computes Cumulative Return, Benchmark Alpha, Annualized Sharpe Ratio, Sortino Ratio, Maximum Drawdown (MDD), Win Rate, and Profit Factor.
  - Generates equity curve series and underwater drawdown plots.
- **Stateful Paper Trading Engine:** Tracks cash, crypto inventory, average cost basis, realized/unrealized PnL, and risk-sized market order fills.
- **Resilient Multi-Tier Data Ingestion:**
  - Binance Vision REST client with exponential backoff and trade window stitching.
  - Headerless Binance tick archive parser & custom CSV loader.
  - Merton Jump-Diffusion market simulator with Hawkes-style order clustering for 100% offline demonstration.
- **Dual Presentation Interfaces:**
  - *Institutional Streamlit Workstation (`app/main.py`):* 7-tab dark workspace with Plotly Candlestick charts, indicator subplots, confusion matrices, and portfolio cards.
  - *Headless CLI (`cli.py`):* Terminal automation for data generation, training, backtesting, and live signaling.

---

## 4. Architecture & Technology Stack

```
+-----------------------------------------------------------------------------------+
|                            USER INTERFACES                                        |
|  +-------------------------------------+  +------------------------------------+  |
|  |     Streamlit Enterprise Workstation |  |     Headless CLI Signal Engine     |  |
|  |   (Live Dashboard, Tabs, Visuals)   |  |   (Automated Training & Backtest)  |  |
|  +-------------------------------------+  +------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            CORE ENGINE PIPELINES                                  |
|                                                                                   |
|  [1. Data Ingestion Layer]                                                        |
|      +-- Binance REST API Client (Resilient retries, trade stitching)             |
|      +-- Binance Vision Tick File Loader (Headerless CSV parser)                  |
|      +-- Synthetic Jump-Diffusion Market Generator (Hawkes / Poisson microstructure)|
|                                                                                   |
|  [2. Microstructure & Feature Engineering Layer]                                  |
|      +-- Time & Volume Bar Aggregator (1s - 60s bars)                             |
|      +-- Order Flow Imbalance (OFI), Volume Delta (CVD), Log Volume               |
|      +-- Multi-Horizon Returns (1, 5, 10, 20 bars) & Realized Volatility          |
|      +-- Technical Indicators: RSI(14), MACD(12,26,9), Bollinger Bands, VWAP     |
|                                                                                   |
|  [3. Quantitative Alpha & Model Engine]                                           |
|      +-- Quantile Labeling (BUY / HOLD / SELL) with custom tail thresholds        |
|      +-- Purged Walk-Forward Time-Series Cross Validation                         |
|      +-- Model Registry: Random Forest, Gradient Boosting, XGBoost, LogReg        |
|      +-- Multi-Class Metric Evaluator: Accuracy, Balanced Acc, F1, ROC-AUC        |
|                                                                                   |
|  [4. Historical Backtesting Simulator]                                            |
|      +-- Event-Driven Signal Simulation                                           |
|      +-- Exchange Transaction Cost Engine (Maker/Taker fees e.g. 0.075%)          |
|      +-- Market Impact & Slippage Modeling (configurable bps)                     |
|      +-- Equity Curve, Sharpe, Sortino, Calmar, Max Drawdown                      |
|                                                                                   |
|  [5. Stateful Paper Portfolio Engine]                                             |
|      +-- Capital Accounting (USDT Cash, Coin Inventory, Total Net Worth)          |
|      +-- Execution Ledger & Trade Fill Tracking                                   |
|      +-- Stop-Loss (SL) & Take-Profit (TP) Risk Management                        |
|                                                                                   |
|  [6. Security & Data Validation Layer]                                            |
|      +-- Input Sanitization & Schema Validation (Pydantic / Typeguard)            |
|      +-- Rate Limiting & Circuit Breaking                                         |
|      +-- Zero-Leakage Data Partitioning                                           |
+-----------------------------------------------------------------------------------+
```

### Technology Stack:
- **Language:** Python 3.12+
- **Data Engineering:** `pandas>=2.2.0`, `numpy>=1.26.0`
- **Machine Learning:** `scikit-learn>=1.4.0`, `xgboost>=2.0.0`
- **Visualization:** `plotly>=5.20.0`, `streamlit>=1.36.0`
- **Network & I/O:** `requests>=2.31.0`, `python-dotenv>=1.0.0`
- **Testing & Quality Assurance:** `pytest>=8.0.0`

---

## 5. Repository Structure

```
miniproject3/
├── .env.example                     # Environment configuration template
├── .gitignore                       # Production git exclusion patterns
├── LICENSE                          # MIT open-source license with attribution
├── README.md                        # Master comprehensive project guide
├── requirements.txt                 # Pinned dependencies with production constraints
├── setup.py                         # Package setup for installable quantpulse module
├── crypto.py                        # Backward-compatible signal engine entrypoint
├── app.py                           # Streamlit dashboard entrypoint
├── cli.py                           # Headless CLI entrypoint for terminal execution
│
├── quantpulse/                      # Core package root
│   ├── __init__.py                  # Package exports and version metadata
│   ├── config.py                    # Centralized, strongly-typed configuration settings
│   ├── data/                        # Ingestion & generation subsystem
│   │   ├── __init__.py
│   │   ├── binance_client.py        # Robust Binance REST client with trade stitching
│   │   ├── csv_loader.py            # Streamlined loader for Binance raw trade CSVs
│   │   └── synthetic.py             # Realistic stochastic jump-diffusion market generator
│   ├── features/                    # Microstructure & technical feature engineering
│   │   ├── __init__.py
│   │   ├── aggregator.py            # Tick-to-bar resampling with buyer/seller maker logic
│   │   ├── indicators.py            # Technical indicators (RSI, MACD, Bollinger, VWAP)
│   │   └── pipeline.py              # End-to-end feature calculation and cleaning
│   ├── models/                      # Machine learning and alpha research
│   │   ├── __init__.py
│   │   ├── labeler.py               # Lookahead return labeling with quantile boundaries
│   │   ├── registry.py              # Factory for Random Forest, Gradient Boost, XGBoost
│   │   ├── trainer.py               # Walk-forward cross validation and fit routines
│   │   └── metrics.py               # Multi-class evaluation (F1, Balanced Acc, Confusion Matrix)
│   ├── backtest/                    # Historical simulation & strategy analytics
│   │   ├── __init__.py
│   │   ├── engine.py                # Vectorized & event-driven simulation with fees/slippage
│   │   └── performance.py           # Financial metrics: Sharpe, Sortino, Max Drawdown
│   ├── paper/                       # Stateful paper portfolio management
│   │   ├── __init__.py
│   │   └── portfolio.py             # Position tracking, cash ledger, risk stops
│   └── security/                    # Validation, resilience, and rate-limiting
│       ├── __init__.py
│       └── validator.py             # Schema verification, NaN handling, API safety
│
├── app/                             # Web presentation layer
│   ├── __init__.py
│   ├── main.py                      # Streamlit dashboard entrypoint
│   ├── styles.py                    # Modular CSS styling and visual components
│   └── visualizer.py                # Plotly financial charts, heatmaps & matrices
│
├── tests/                           # Complete automated test suite (23 tests)
│   ├── __init__.py
│   ├── test_data.py                 # Tests for loaders, API client, and synthetic generator
│   ├── test_features.py             # Tests for bar aggregation and indicators
│   ├── test_models.py               # Tests for model training, labeling, and metrics
│   ├── test_backtest.py             # Tests for transaction costs and performance analytics
│   ├── test_portfolio.py            # Tests for paper trading state and order execution
│   └── test_security.py             # Tests for input validation and error recovery
│
└── docs/                            # Comprehensive engineering documentation
    ├── REPOSITORY_AUDIT.md          # In-depth audit of reference repository
    ├── ARCHITECTURE.md              # System design and component specifications
    ├── IMPROVEMENT_ROADMAP.md       # Roadmap of implemented and future enhancements
    ├── EVALUATION_REPORT.md         # Quantitative evaluation, metrics, and benchmarks
    ├── CHANGELOG.md                 # Granular version and modification history
    └── FINAL_REPORT.md              # Verification report and production handoff
```

---

## 6. Windows Installation Instructions

### Prerequisites
- Windows 10 or 11
- PowerShell 5.1+ or PowerShell 7+
- Python 3.12 (or 3.9+)
- Git for Windows

### Step-by-Step Setup
1. Clone destination repository:
   ```powershell
   git clone https://github.com/drx2k06/miniproject3.git "$HOME\Projects\miniproject3"
   cd "$HOME\Projects\miniproject3"
   ```

2. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install project dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Install the package in editable mode:
   ```powershell
   python -m pip install -e .
   ```

---

## 7. Environment Configuration

Copy the template configuration file:
```powershell
copy .env.example .env
```

Key variables configured in `.env`:
```ini
# Binance Public Vision REST Endpoint (Free, no key required)
BINANCE_BASE=https://data-api.binance.vision
SYMBOL=BTCUSDT

# Bar Aggregation & Lookahead
BAR_SECONDS=1
PREDICT_AHEAD=10
TAIL_QUANTILE=0.25
TEST_SPLIT=0.30

# Simulated Exchange Frictions
TAKER_FEE=0.00075    # 0.075% taker fee
SLIPPAGE=0.00050     # 5 basis points

# Paper Trading Capital
PAPER_CASH=10000.0
RISK_PCT=10.0
```

---

## 8. Commands to Run the Application

### 8.1 Launching the Interactive Streamlit Workstation
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501` to explore all 7 workstation tabs.

### 8.2 Running the Headless CLI
QuantPulse provides a powerful CLI (`cli.py`):
```powershell
# 1. Train and benchmark all ML models with Walk-Forward CV
python cli.py train --trades 35000

# 2. Run historical strategy backtest with fees and slippage
python cli.py backtest --model "Gradient Boosting" --capital 10000 --fee 0.00075 --slippage 0.0005

# 3. Poll live Binance signal
python cli.py live-signal --symbol BTCUSDT

# 4. Generate synthetic tick dataset
python cli.py generate-data --output btc_ticks.csv --trades 30000
```

### 8.3 Running the Backward-Compatible Signal Engine
```powershell
python crypto.py
```

---

## 9. Commands to Run Tests

Run the full automated test suite using `pytest`:
```powershell
python -m pytest -v
```

All 23 unit and integration tests execute in $\approx 4.3$ seconds with zero errors:
```
tests/test_backtest.py::test_calculate_financial_metrics PASSED
tests/test_backtest.py::test_backtest_engine_run PASSED
tests/test_data.py::test_synthetic_market_generator PASSED
tests/test_data.py::test_trade_data_loader_custom_csv PASSED
tests/test_data.py::test_trade_data_loader_binance_vision_format PASSED
tests/test_data.py::test_trade_data_loader_empty_file PASSED
tests/test_features.py::test_to_bars PASSED
tests/test_features.py::test_microstructure_flow PASSED
tests/test_features.py::test_rsi_bounds PASSED
tests/test_features.py::test_macd PASSED
tests/test_features.py::test_bollinger_bands PASSED
tests/test_features.py::test_compute_features_pipeline PASSED
tests/test_features.py::test_legacy_features_compatibility PASSED
tests/test_models.py::test_create_labels PASSED
tests/test_models.py::test_evaluate_classification PASSED
tests/test_models.py::test_get_models PASSED
tests/test_models.py::test_model_trainer_walk_forward PASSED
tests/test_models.py::test_legacy_train_tuple_unpacking PASSED
tests/test_portfolio.py::test_paper_portfolio_lifecycle PASSED
tests/test_portfolio.py::test_paper_plan_strings PASSED
tests/test_security.py::test_validate_csv_upload_size_limit PASSED
tests/test_security.py::test_sanitize_financial_dataframe PASSED
tests/test_security.py::test_verify_numeric_bounds PASSED

============================= 23 passed in 4.30s ==============================
```

---

## 10. API & Code Usage Examples

### 10.1 Generating Data, Resampling Bars, and Computing Features
```python
from quantpulse.data.synthetic import generate_synthetic_trades
from quantpulse.features.aggregator import to_bars
from quantpulse.features.pipeline import compute_features

# 1. Generate high-frequency tick events
trades = generate_synthetic_trades(n_trades=20000)

# 2. Resample into 1-second time bars
bars = to_bars(trades, sec=1)

# 3. Compute 18 microstructure & technical features
feat_df = compute_features(bars, mode="full").dropna()
print(f"Computed {len(feat_df)} bars with columns: {list(feat_df.columns)}")
```

### 10.2 Training Walk-Forward Models & Evaluating
```python
from quantpulse.models.registry import get_models
from quantpulse.models.trainer import ModelTrainer

models = get_models()
gb = models["Gradient Boosting"]

result = ModelTrainer.train(feat_df, gb, ahead=10, tail=0.25, test_ratio=0.30)
print(f"Accuracy: {result.accuracy:.3f} | Baseline: {result.baseline:.3f}")
print(f"Balanced Acc: {result.metrics['balanced_accuracy']:.3f} | Macro F1: {result.metrics['f1_macro']:.3f}")
```

### 10.3 Running a Historical Backtest with Exchange Frictions
```python
from quantpulse.backtest.engine import BacktestEngine

engine = BacktestEngine(
    fee_rate=0.00075,      # 0.075% taker fee
    slippage_rate=0.0005,  # 5 bps slippage
    initial_capital=10000.0,
)
bt_res = engine.run(result.test_data, signal_col="prediction")
print(f"Strategy Return: {bt_res.metrics['strategy_return']:+.2%}")
print(f"Benchmark Return: {bt_res.metrics['benchmark_return']:+.2%}")
print(f"Alpha: {bt_res.metrics['alpha']:+.2%}")
print(f"Sharpe Ratio: {bt_res.metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {bt_res.metrics['max_drawdown']:.2%}")
```

### 10.4 Managing Stateful Paper Portfolio Orders
```python
from quantpulse.paper.portfolio import PaperPortfolio

port = PaperPortfolio(initial_cash=10000.0)
rec = port.execute(action="BUY", price=65000.0, risk_pct=10.0)
print(f"Bought {rec.quantity:.6f} coins at ${rec.price:,.2f}. Cash remaining: ${port.cash:,.2f}")
```

---

## 11. Data Sources & Update Frequency

1. **Binance Public Vision REST API (`https://data-api.binance.vision`):**
   - Public, free, read-only endpoint requiring zero API keys.
   - Endpoint: `/api/v3/trades?symbol=BTCUSDT&limit=1000`.
   - Update Frequency: Sub-second tick updates upon manual or scheduled polling.
2. **Local Binance Daily Trade Archives:**
   - Supports official headerless daily `.csv` files containing trade IDs, microsecond timestamps, quantities, and maker flags.
3. **Merton Jump-Diffusion Synthetic Generator:**
   - Deterministic or stochastic offline tick stream generator for reproducible continuous testing without external network dependencies.

---

## 12. Quantitative Evaluation & Measured Results

| Evaluation Metric | Baseline Reference Prototype | QuantPulse Re-Engineered Platform | Engineering Significance |
|---|---|---|---|
| **ML Models Evaluated** | 2 basic models (DT, RF) | 5 models (RF, GB, XGBoost, LogReg, DT) | Comprehensive linear & non-linear comparison |
| **Model Accuracy (GB / XGB)** | $37.6\% - 38.9\%$ | **$46.6\% - 46.9\%$** | **$+8.0\%$ to $+9.3\%$ absolute improvement** |
| **Multi-Class Metrics** | None (only scalar accuracy) | Balanced Acc, Macro F1, Confusion Matrix | Guards against majority-class deception |
| **Cross-Validation** | Static split | Purged Walk-Forward Time-Series Split | Zero lookahead bias / data leakage |
| **Backtest Engine** | Non-existent ($0$ metrics) | Full fee & slippage simulator | Calculates true net Sharpe, Sortino, MDD |
| **Backtest Alpha (Bear Phase)**| N/A | **$+0.91\%$ Excess Return** | Strategy capital preservation in downtrend |
| **Maximum Drawdown** | N/A | **12.86% vs 18.40% benchmark** | **$-5.54\%$ risk reduction** |
| **Paper Trading State** | Static string formatter | Full ledger (Cash, Coin, Cost Basis, PnL) | True forward-testing execution environment |
| **Automated Tests** | 0 tests ($0\%$) | **23 tests ($100\%$ passing)** | Mathematical verification & zero regressions |

*(See [`docs/EVALUATION_REPORT.md`](docs/EVALUATION_REPORT.md) for complete experimental methodology and confusion matrices).*

---

## 13. Security Considerations

- **Zero Hardcoded Credentials:** The application does not store, hardcode, or require private keys, exchange secret keys, or wallet seed phrases. All public market queries utilize read-only REST endpoints.
- **Environment Isolation:** `.env.example` is provided as a placeholder template. `.gitignore` strictly excludes `.env`, credential files, local database files, and tick data caches.
- **Network Resilience:** External requests to Binance incorporate exponential backoff, connection timeouts (10 seconds), and circuit breaking to prevent rate-limit bans (`HTTP 429`).
- **Input Validation:** User-uploaded CSV files are screened by `validate_csv_upload` to enforce a 100MB buffer limit and verify proper schema structure before memory allocation.
- **Financial Risk Safeguards:** All backtests explicitly model exchange fees and slippage to prevent over-optimistic return claims. Educational disclaimers are prominent throughout the UI.

---

## 14. Limitations & Future Improvements

1. **Level-2 Limit Order Book (LOB) Queue Dynamics:** Currently, the system operates on executed trades. Adding WebSocket L2 depth streams (`/ws/btcusdt@depth20`) will enable computing order book imbalance and micro-price slope.
2. **Dynamic Volatility Thresholds:** Implementing volatility-adjusted quantile labeling (e.g. triple barrier method) will enhance label robustness during sudden volatility spikes.
3. **Multi-Asset Portfolio Arbitrage:** Extending the execution engine to multi-pair baskets and perpetual futures funding rate arbitrage.

---

## 15. Original Repository Attribution & Licensing

### Original Prototype Attribution
- **Repository:** [`https://github.com/Divya-25-C/crypto_project.git`](https://github.com/Divya-25-C/crypto_project.git)
- **Author:** **Divya-25-C**
- **Reference Commit:** `b3809d3ad2e8f748449f9c145a4f7bb9525768c9`
- **Initial Concept:** Supervised classification of trade order flow using Streamlit and scikit-learn.

### Applicable Licensing
This customized re-engineered project is licensed under the **MIT License**.  
See the [`LICENSE`](LICENSE) file for complete terms and copyright notices.

---

## 16. Developer & Engineering Contributions

**Daniel Richard Xavier** led the architectural re-engineering and quantitative development of QuantPulse:
- **System Architecture:** Designed the modular package structure (`quantpulse`) separating ingestion, feature engineering, modeling, backtesting, portfolio management, and security.
- **Microstructure Feature Engineering:** Developed 18 high-frequency features including Order Flow Imbalance (OFI), Cumulative Volume Delta (CVD), and VWAP distance.
- **Machine Learning & Validation:** Implemented purged walk-forward time-series cross-validation, multi-class balanced scoring, and gradient boosting/XGBoost pipelines.
- **Quantitative Backtesting Simulator:** Built the transaction cost and slippage simulation engine, equity curve generator, and risk KPI scorecard.
- **Stateful Paper Trading Engine:** Engineered `PaperPortfolio` to simulate real-time capital allocation, position sizing, and execution auditing.
- **Institutional UI/UX:** Designed and built the 7-tab Streamlit dashboard with custom CSS, Plotly candlestick charts, and financial indicators.
- **Quality Assurance & Verification:** Created the 23-test automated test suite and authored the comprehensive documentation suite.
