"""QuantPulse CLI - Unified Terminal Command-Line Interface.

Developed by Daniel Richard Xavier.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from quantpulse.backtest.engine import BacktestEngine
from quantpulse.config import default_config
from quantpulse.data.binance_client import BinanceClient
from quantpulse.data.csv_loader import load_trades
from quantpulse.data.synthetic import generate_synthetic_trades
from quantpulse.features.aggregator import to_bars
from quantpulse.features.pipeline import compute_features
from quantpulse.models.registry import get_models
from quantpulse.models.trainer import ModelTrainer
from quantpulse.paper.portfolio import PaperPortfolio, paper_plan


def get_bars_or_generate(filepath: str | None = None, n_trades: int = 35000) -> pd.DataFrame:
    """Helper to load bars from file or generate synthetic benchmark."""
    if filepath and Path(filepath).exists():
        print(f"[*] Reading trade data from: {filepath}")
        raw = load_trades(filepath)
    else:
        print(f"[*] Simulating {n_trades:,} realistic trades using Merton Jump-Diffusion...")
        raw = generate_synthetic_trades(n_trades=n_trades)
    
    bars = to_bars(raw, sec=1)
    bars = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
    print(f"[+] Formed {len(bars):,} 1-second feature bars.")
    return bars


def cmd_generate(args):
    """Generate synthetic trade CSV."""
    output_path = Path(args.output)
    print(f"[*] Generating {args.trades:,} synthetic trades to {output_path}...")
    df = generate_synthetic_trades(n_trades=args.trades, seed=args.seed)
    df.to_csv(output_path, index=False)
    print(f"[✓] Saved {len(df):,} trades to {output_path.resolve()}.")


def cmd_train(args):
    """Train models and print comprehensive performance metrics."""
    bars = get_bars_or_generate(args.data, n_trades=args.trades)
    models = get_models()

    print("\n" + "=" * 80)
    print("  QUANTPULSE MULTI-MODEL QUANTITATIVE EVALUATION (WALK-FORWARD CV)")
    print("=" * 80)
    print(f"{'Model Name':<22} | {'Accuracy':<9} | {'Baseline':<9} | {'Bal Acc':<9} | {'Macro F1':<9} | {'Edge':<9}")
    print("-" * 80)

    for name, model in models.items():
        res = ModelTrainer.train(bars, model, ahead=args.ahead, tail=args.tail, test_ratio=0.30)
        edge = res.accuracy - res.baseline
        edge_str = f"{edge:+.3f}"
        print(f"{name:<22} | {res.accuracy:.3f}     | {res.baseline:.3f}     | {res.metrics['balanced_accuracy']:.3f}     | {res.metrics['f1_macro']:.3f}     | {edge_str:<9}")

    print("=" * 80)


def cmd_backtest(args):
    """Run historical backtest with fee and slippage modeling."""
    bars = get_bars_or_generate(args.data, n_trades=args.trades)
    models = get_models()
    model = models.get(args.model, models["Random Forest"])

    print(f"\n[*] Training {args.model} for backtesting...")
    res = ModelTrainer.train(bars, model, ahead=10, tail=0.25, test_ratio=0.30)

    engine = BacktestEngine(
        fee_rate=args.fee,
        slippage_rate=args.slippage,
        initial_capital=args.capital,
    )
    result = engine.run(res.test_data, signal_col="prediction")
    m = result.metrics

    print("\n" + "=" * 60)
    print("  STRATEGY BACKTEST SCORECARD (WITH FEES & SLIPPAGE)")
    print("=" * 60)
    print(f"  Initial Capital:       ${result.initial_capital:,.2f}")
    print(f"  Final Capital:         ${result.final_capital:,.2f}")
    print(f"  Strategy Return:       {m['strategy_return']:+.2%}")
    print(f"  Benchmark Return:      {m['benchmark_return']:+.2%}")
    print(f"  Alpha (Excess):        {m['alpha']:+.2%}")
    print(f"  Sharpe Ratio:          {m['sharpe_ratio']:.2f}")
    print(f"  Sortino Ratio:         {m['sortino_ratio']:.2f}")
    print(f"  Maximum Drawdown:      {m['max_drawdown']:.2%}")
    print(f"  Total Trades:          {m['trade_count']}")
    print(f"  Win Rate:              {m['win_rate']:.1%}")
    print(f"  Profit Factor:         {m['profit_factor']:.2f}")
    print("=" * 60)


def cmd_live(args):
    """Poll live Binance Vision data and produce model recommendation."""
    client = BinanceClient(base_url=default_config.binance_base_url)
    print(f"[*] Polling live trade flow for {args.symbol} from Binance...")
    try:
        trades = client.fetch_trades(symbol=args.symbol, limit=1000)
    except Exception as e:
        print(f"[!] Live query failed ({e}). Falling back to synthetic micro-feed.")
        trades = generate_synthetic_trades(n_trades=1000)

    bars = to_bars(trades, sec=args.sec)
    feat_df = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)
    if feat_df.empty:
        print("[!] Insufficient bars. Generating context buffer...")
        synth = generate_synthetic_trades(n_trades=2500)
        bars = to_bars(synth, sec=args.sec)
        feat_df = compute_features(bars, mode="full").dropna(subset=default_config.baseline_features)

    models = get_models()
    rf = models["Random Forest"]
    # Train on current bars or synthetic reference
    res = ModelTrainer.train(feat_df, rf, ahead=10, tail=0.25, test_ratio=0.30)
    last_row = feat_df.iloc[[-1]]
    feats = [f for f in default_config.baseline_features if f in last_row.columns]
    p = rf.predict_proba(last_row[feats])[0]
    pred_cls = int(rf.classes_[p.argmax()])
    sig_name = default_config.label_names.get(pred_cls, "HOLD")
    price = float(last_row["price"].iloc[0])

    print("\n" + "=" * 50)
    print(f"  LIVE SIGNAL: {sig_name}  (Confidence: {p.max():.1%})")
    print(f"  Current Price: ${price:,.2f}")
    print(f"  Paper Plan:    {paper_plan(sig_name, price, cash=1000.0, risk_pct=10)}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="QuantPulse CLI - Crypto Quantitative Signal Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate-data
    p_gen = subparsers.add_parser("generate-data", help="Generate synthetic trade stream CSV")
    p_gen.add_argument("--output", "-o", default="synthetic_trades.csv", help="Output CSV path")
    p_gen.add_argument("--trades", "-n", type=int, default=30000, help="Number of trades")
    p_gen.add_argument("--seed", type=int, default=42, help="Random seed")
    p_gen.set_defaults(func=cmd_generate)

    # Subcommand: train
    p_train = subparsers.add_parser("train", help="Train and benchmark ML models")
    p_train.add_argument("--data", "-d", default=None, help="Path to trade CSV")
    p_train.add_argument("--trades", "-n", type=int, default=35000, help="Synthetic trades if no data")
    p_train.add_argument("--ahead", type=int, default=10, help="Future prediction horizon bars")
    p_train.add_argument("--tail", type=float, default=0.25, help="Quantile cutoff for Buy/Sell")
    p_train.set_defaults(func=cmd_train)

    # Subcommand: backtest
    p_bt = subparsers.add_parser("backtest", help="Run historical strategy backtest with fees")
    p_bt.add_argument("--data", "-d", default=None, help="Path to trade CSV")
    p_bt.add_argument("--trades", "-n", type=int, default=35000, help="Synthetic trades if no data")
    p_bt.add_argument("--model", "-m", default="Random Forest", help="Model name")
    p_bt.add_argument("--capital", "-c", type=float, default=10000.0, help="Initial capital in USDT")
    p_bt.add_argument("--fee", type=float, default=0.00075, help="Taker fee rate (default: 0.075%)")
    p_bt.add_argument("--slippage", type=float, default=0.0005, help="Slippage rate (default: 5 bps)")
    p_bt.set_defaults(func=cmd_backtest)

    # Subcommand: live-signal
    p_live = subparsers.add_parser("live-signal", help="Fetch live Binance trades and predict signal")
    p_live.add_argument("--symbol", "-s", default="BTCUSDT", help="Pair symbol")
    p_live.add_argument("--sec", type=int, default=1, help="Bar seconds")
    p_live.set_defaults(func=cmd_live)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
