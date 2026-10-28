# QuantPulse Platform Architecture & Technical Design Specification

**System Name:** QuantPulse Crypto Signal & Quantitative Analytics Engine  
**Developer:** Daniel Richard Xavier  
**Original Reference Concept:** Stream Light by Divya-25-C  
**Version:** 2.0.0 (Production Architecture)  
**Date:** October 2026  

---

## 1. High-Level Architectural Vision

QuantPulse is an enterprise-grade cryptocurrency intelligence, quantitative alpha modeling, and paper trading platform. It advances the conceptual foundation of the original "Stream Light" prototype into a production-ready, modular system featuring resilient data ingestion, advanced microstructure feature engineering, leak-free walk-forward machine learning, realistic transaction cost backtesting, and a stateful portfolio simulation engine.

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

---

## 2. Directory & Package Structure

The project has been restructured from a monolithic two-file script into an extensible, object-oriented package hierarchy:

```
miniproject3/
├── .env.example                     # Environment configuration template
├── .gitignore                       # Production git exclusion patterns
├── LICENSE                          # MIT open-source license with attribution
├── README.md                        # Master comprehensive project guide
├── requirements.txt                 # Pinned dependencies with production constraints
├── setup.py                         # Package setup for installable quantpulse module
│
├── quantpulse/                      # Core package root
│   ├── __init__.py                  # Package exports and version metadata
│   ├── config.py                    # Centralized, strongly-typed configuration settings
│   │
│   ├── data/                        # Ingestion & generation subsystem
│   │   ├── __init__.py
│   │   ├── binance_client.py        # Robust Binance REST client with trade stitching
│   │   ├── csv_loader.py            # Streamlined loader for Binance raw trade CSVs
│   │   └── synthetic.py             # Realistic stochastic jump-diffusion market generator
│   │
│   ├── features/                    # Microstructure & technical feature engineering
│   │   ├── __init__.py
│   │   ├── aggregator.py            # Tick-to-bar resampling with buyer/seller maker logic
│   │   ├── indicators.py            # Technical indicators (RSI, MACD, Bollinger, VWAP)
│   │   └── pipeline.py              # End-to-end feature calculation and cleaning
│   │
│   ├── models/                      # Machine learning and alpha research
│   │   ├── __init__.py
│   │   ├── labeler.py               # Lookahead return labeling with quantile boundaries
│   │   ├── registry.py              # Factory for Random Forest, Gradient Boost, XGBoost
│   │   ├── trainer.py               # Walk-forward cross validation and fit routines
│   │   └── metrics.py               # Multi-class evaluation (F1, Balanced Acc, Confusion Matrix)
│   │
│   ├── backtest/                    # Historical simulation & strategy analytics
│   │   ├── __init__.py
│   │   ├── engine.py                # Vectorized & event-driven simulation with fees/slippage
│   │   └── performance.py           # Financial metrics: Sharpe, Sortino, Max Drawdown
│   │
│   ├── paper/                       # Stateful paper portfolio management
│   │   ├── __init__.py
│   │   └── portfolio.py             # Position tracking, cash ledger, risk stops
│   │
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
├── cli.py                           # Headless CLI entrypoint for terminal execution
│
├── tests/                           # Complete automated test suite
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

## 3. Detailed Component Specifications

### 3.1 Data Ingestion & Microstructure Resampling (`quantpulse.data`)
- **`BinanceClient`**: Interacts with the public Binance REST API. Unlike the reference repository which was limited to requesting 1,000 trades once, `BinanceClient` implements:
  - Iterative trade stitching using `fromId` pagination to collect at least 3,000–5,000 recent trades across a sliding window.
  - Automatic exponential backoff (`HTTP 429` / `5xx` mitigation).
  - Graceful fallback to offline cached data or synthetic simulation when the network is restricted.
- **`SyntheticMarketGenerator`**: Produces statistically realistic cryptocurrency tick streams using:
  - Geometric Brownian Motion drift with Merton Jump-Diffusion shocks ($\lambda=0.05$).
  - Hawkes-style order flow clustering where aggressive buy/sell orders arrive in correlated bursts.
  - Generates full order attributes: `timestamp`, `price`, `quantity`, `is_buyer_maker`.

### 3.2 Microstructure & Alpha Feature Engineering (`quantpulse.features`)
- **Resampling (`Aggregator`)**: Converts uneven high-frequency trade ticks into uniform time bars ($1\text{s}, 5\text{s}, 10\text{s}, 30\text{s}, 60\text{s}$). For each bar, computes:
  - Open, High, Low, Close (OHLC)
  - Total traded volume ($V$) and Trade count ($N$)
  - Buy volume ($V_{\text{buy}}$) and Sell volume ($V_{\text{sell}}$)
- **Feature Suite (Expanded to 18 indicators)**:
  1. `ret_1`, `ret_5`, `ret_10`, `ret_20`: Multi-horizon percentage price changes.
  2. `vol_20`, `vol_60`: Rolling annualized/scaled price volatility.
  3. `flow`: Order Flow Imbalance: $\text{OFI} = \frac{V_{\text{buy}} - V_{\text{sell}}}{V_{\text{total}}} \in [-1.0, 1.0]$.
  4. `flow_5`, `flow_20`: Short-term and medium-term moving average order flow.
  5. `cvd`: Cumulative Volume Delta across the session.
  6. `log_qty`: Log-transformed trade volume: $\ln(1 + V)$.
  7. `vwap`: Volume Weighted Average Price: $\text{VWAP} = \frac{\sum (P_i \times V_i)}{\sum V_i}$.
  8. `vwap_dist`: Normalized distance of current price from VWAP: $(P - \text{VWAP}) / \text{VWAP}$.
  9. `rsi_14`: Relative Strength Index computed via Wilder's smoothing.
  10. `macd_line`, `macd_signal`, `macd_hist`: Moving Average Convergence Divergence (12, 26, 9).
  11. `bb_upper`, `bb_lower`, `bb_pct_b`: Bollinger Bands (20 periods, 2 standard deviations).

### 3.3 Quantitative Alpha & Model Engine (`quantpulse.models`)
- **Labeling Protocol**: Computes forward return $R_{t, t+k} = \frac{P_{t+k}}{P_t} - 1$.
  - Uses training set quantile thresholds ($\tau = 0.25$ or user configurable):
    - $\text{BUY (2)}$: $R_{t, t+k} > Q_{1-\tau}$
    - $\text{SELL (0)}$: $R_{t, t+k} < Q_{\tau}$
    - $\text{HOLD (1)}$: $Q_{\tau} \le R_{t, t+k} \le Q_{1-\tau}$
- **Model Portfolio**:
  - `RandomForestClassifier`: Optimized with `min_samples_leaf=5`, balanced class weighting, and parallelized execution.
  - `GradientBoostingClassifier` / `XGBClassifier`: Depth-constrained, regularization penalties, learning rate calibration.
  - `LogisticRegression`: Scaled baseline model providing linear benchmark.
- **Validation Discipline**:
  - Chronological walk-forward split (train on past, test on subsequent unseen period).
  - Metrics: Accuracy, Balanced Accuracy, Precision, Recall, Macro F1, Weighted F1, Confusion Matrix.

### 3.4 Realistic Backtesting Engine (`quantpulse.backtest`)
- **Execution Model**:
  - Translates model signals (`BUY`, `HOLD`, `SELL`) into positions.
  - Applies transaction fee deducted directly from portfolio cash balance (default: 7.5 basis points or $0.075\%$).
  - Applies slippage penalty (default: 5 basis points or $0.05\%$).
- **Performance Output**:
  - Cumulative Strategy Return vs Buy & Hold Benchmark Return.
  - Sharpe Ratio ($Rf = 0\%$), Sortino Ratio (penalizing only downside volatility).
  - Maximum Drawdown (MDD) and Drawdown Duration.
  - Win Rate (% profitable trades) and Profit Factor ($\frac{\sum \text{Gains}}{\sum \text{Losses}}$).

### 3.5 Stateful Paper Trading Simulator (`quantpulse.paper`)
- Persistent object model:
  ```python
  class PaperPortfolio:
      cash: float          # USDT cash available
      coin_qty: float      # Crypto coins currently held
      avg_entry_price: float
      trade_history: List[TradeRecord]
      realized_pnl: float
      unrealized_pnl: float
  ```
- Implements position sizing: Risk fixed percentage ($X\%$) of total portfolio equity per trade.
- Tracks execution timestamps, slippage, and fees.
- Provides risk stop safeguards: automatic stop-loss liquidations if adverse price movement exceeds threshold.

---

## 4. UI/UX System Redesign

The user interface has been completely transformed into an interactive workstation:
1. **Header Bar**: Live status indicator, market regime badges, BTC/USDT price ticker with delta.
2. **Unified Navigation Tabs**:
   - *Tab 1: Live Market & Signals*: Candlestick chart with Bollinger Bands and VWAP overlays, real-time prediction card with confidence gauge, paper order plan.
   - *Tab 2: Technical Indicators & Microstructure*: Interactive RSI, MACD, and Order Flow Imbalance graphs.
   - *Tab 3: Model Training & Evaluation*: Walk-forward accuracy vs baseline, multi-class metrics table, feature importance ranking.
   - *Tab 4: Strategy Backtesting Studio*: Strategy equity curve vs Buy & Hold, drawdown underwater plot, financial KPI scorecard.
   - *Tab 5: Paper Trading Portfolio*: Balance dashboard, live PnL, active position status, chronological execution ledger.
   - *Tab 6: Data Workbench*: Switch between Live Binance API, Uploaded CSV, or Realistic Synthetic Generator.
3. **Accessibility & Design System**:
   - Modern dark/light theme with slate backgrounds (`#0B1118`, `#16202C`), emerald green alpha accents (`#10B981`), coral risk indicators (`#EF4444`), and high-contrast typography.
