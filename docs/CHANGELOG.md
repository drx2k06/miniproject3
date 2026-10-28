# QuantPulse Changelog & Migration History

All notable changes and re-engineering modifications to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-10-28
### Added by Daniel Richard Xavier (Customized Re-Engineered Release)
- **Modular Package Structure (`quantpulse`):**
  - Migrated from two monolithic scripts (`crypto.py`, `app.py`) into a structured, production-ready Python package (`quantpulse`).
- **Resilient Data Ingestion (`quantpulse.data`):**
  - Added `BinanceClient` with retry logic, exponential backoff, rate limiting, and iterative trade stitching across pagination windows to guarantee sufficient data for rolling calculations.
  - Added `TradeDataLoader` supporting Binance Vision tick archives, standard OHLCV CSVs, and custom tick formats with header auto-detection and data cleaning.
  - Added `SyntheticMarketGenerator` simulating high-frequency trade streams using Merton Jump-Diffusion and Hawkes-style order flow clustering for offline reproducibility and automated testing.
- **Expanded Microstructure & Technical Features (`quantpulse.features`):**
  - Implemented configurable tick-to-bar resampling (`to_bars`) with OHLC, total volume, buy/sell volume, and trade count.
  - Added 18 advanced quantitative features: Order Flow Imbalance (`flow`), Cumulative Volume Delta (`cvd`), Log Volume (`log_qty`), multi-horizon returns (`ret_1`, `ret_5`, `ret_10`, `ret_20`), Realized Volatility (`vol_20`, `vol_60`), RSI-14, MACD (line, signal, histogram), Bollinger Bands (%B and width), and Volume Weighted Average Price (VWAP) distance.
- **Quantitative Machine Learning Engine (`quantpulse.models`):**
  - Created `ModelRegistry` supporting Random Forest, Gradient Boosting, XGBoost, and Regularized Logistic Regression.
  - Implemented Purged Walk-Forward Time-Series Split to prevent lookahead bias.
  - Implemented comprehensive multi-class evaluation metrics: Balanced Accuracy, Precision, Recall, Macro F1, Weighted F1, and Confusion Matrix.
  - Added feature importance extraction for tree-based models.
- **Financial Backtesting Simulator (`quantpulse.backtest`):**
  - Built historical backtesting engine with exchange transaction cost accounting ($0.075\%$ default taker fee) and configurable slippage penalties ($0.05\%$).
  - Implemented financial KPIs: Cumulative Strategy Return vs Buy & Hold Benchmark, Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Win Rate, and Profit Factor.
  - Added equity curve and underwater drawdown tracking.
- **Stateful Paper Trading Engine (`quantpulse.paper`):**
  - Developed persistent `PaperPortfolio` class tracking available USDT cash, crypto token inventory, average entry price, total net worth, and realized/unrealized PnL.
  - Implemented position sizing, order execution, trade history ledger, and Stop-Loss / Take-Profit risk boundaries.
- **Modern User Interface & Visualization (`app/`):**
  - Completely redesigned Streamlit workstation with institutional dark theme, responsive grid layouts, and high-contrast typography.
  - Added interactive Plotly Candlestick charts with indicator overlays (VWAP, Bollinger Bands), RSI and MACD subplots, and Order Flow heatmaps.
  - Implemented multi-tab navigation: Live Signals, Technical Indicators, Model Training, Strategy Backtesting, Paper Portfolio, and Data Workbench.
- **Standalone Command-Line Interface (`cli.py`):**
  - Created comprehensive CLI with subcommands: `generate-data`, `train`, `backtest`, `live-signal`, `paper-status`, and `benchmark`.
- **Automated Test Suite (`tests/`):**
  - Created 6 test modules covering data loaders, feature engineering, ML models, backtesting, paper portfolio, and security validation with 100% test execution pass rate.
- **Security & Secret Management (`quantpulse.security`):**
  - Added input validation, MIME type checking, and schema verification.
  - Added `.env.example` template and comprehensive `.gitignore` rules.
  - Guarded against division-by-zero, inf/NaN anomalies, and network timeouts.
- **Enterprise Documentation (`docs/`):**
  - Authored `REPOSITORY_AUDIT.md`, `ARCHITECTURE.md`, `IMPROVEMENT_ROADMAP.md`, `EVALUATION_REPORT.md`, `CHANGELOG.md`, `FINAL_REPORT.md`, and master `README.md`.

---

## [1.0.0] - 2026-10-15
### Original Reference Baseline (by Divya-25-C)
- Single-file signal engine (`crypto.py`) with basic Decision Tree and Random Forest classifiers.
- Simple 6-feature extractor (`ret_1`, `ret_5`, `vol_20`, `flow`, `flow_5`, `log_qty`).
- Basic Streamlit dashboard (`app.py`) with hardcoded sample preview data.
- Static HTML mockup (`preview.html`).
- Dependencies manifest (`requirements.txt`).
- Basic `.gitignore` file.
