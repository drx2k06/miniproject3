"""Tests for data ingestion, synthetic market generation, and CSV loading."""
import io
import pandas as pd
import pytest

from quantpulse.data.binance_client import BinanceClient
from quantpulse.data.csv_loader import TradeDataLoader, load_trades
from quantpulse.data.synthetic import SyntheticMarketGenerator, generate_synthetic_trades


def test_synthetic_market_generator():
    gen = SyntheticMarketGenerator(start_price=60000.0, seed=123)
    df = gen.generate(n_trades=1000)

    assert not df.empty
    assert len(df) == 1000
    assert list(df.columns) == ["timestamp", "price", "quantity", "side"]
    assert (df["price"] > 0).all()
    assert (df["quantity"] > 0).all()
    assert set(df["side"].unique()).issubset({"buy", "sell"})
    assert pd.to_datetime(df["timestamp"]).is_monotonic_increasing


def test_trade_data_loader_custom_csv():
    csv_content = """timestamp,price,quantity,side
2026-10-15 10:00:00,60000.5,1.2,buy
2026-10-15 10:00:01,60001.0,0.5,sell
2026-10-15 10:00:02,60002.0,2.1,buy
"""
    stream = io.StringIO(csv_content)
    df = TradeDataLoader.load(stream)

    assert len(df) == 3
    assert list(df.columns) == ["timestamp", "price", "quantity", "side"]
    assert df["price"].iloc[0] == 60000.5
    assert df["side"].iloc[1] == "sell"


def test_trade_data_loader_binance_vision_format():
    # Binance Vision headerless format: id, price, qty, quote_qty, time_ms, is_buyer_maker, is_best_match
    csv_content = """1001,65000.50,0.150,9750.075,1728986400000,true,true
1002,65001.00,0.200,13000.200,1728986401000,false,true
"""
    stream = io.StringIO(csv_content)
    df = load_trades(stream)

    assert len(df) == 2
    assert "timestamp" in df.columns
    # maker=true -> sell, maker=false -> buy
    assert df["side"].iloc[0] == "sell"
    assert df["side"].iloc[1] == "buy"


def test_trade_data_loader_empty_file():
    stream = io.StringIO("")
    df = TradeDataLoader.load(stream)
    assert df.empty
    assert list(df.columns) == ["timestamp", "price", "quantity", "side"]
