"""Tests for bar aggregation and microstructure feature calculation."""
import pandas as pd
import numpy as np
import pytest

from quantpulse.data.synthetic import generate_synthetic_trades
from quantpulse.features.aggregator import to_bars
from quantpulse.features.indicators import (
    calculate_bollinger_bands,
    calculate_macd,
    calculate_microstructure_flow,
    calculate_rsi,
    calculate_vwap,
)
from quantpulse.features.pipeline import compute_features, features


@pytest.fixture
def sample_trades():
    return generate_synthetic_trades(n_trades=2000, seed=42)


def test_to_bars(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    assert not bars.empty
    expected_cols = ["timestamp", "price", "open", "high", "low", "close", "qty", "buy", "sell", "n"]
    for col in expected_cols:
        assert col in bars.columns

    # High should be >= Low
    assert (bars["high"] >= bars["low"]).all()
    # Quantity should equal buy + sell
    np.testing.assert_allclose(bars["qty"], bars["buy"] + bars["sell"], rtol=1e-5)


def test_microstructure_flow(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    flow_df = calculate_microstructure_flow(bars)

    assert "flow" in flow_df.columns
    assert "cvd" in flow_df.columns
    assert "log_qty" in flow_df.columns
    # Order flow imbalance must be bounded [-1.0, 1.0]
    assert (flow_df["flow"] >= -1.0).all()
    assert (flow_df["flow"] <= 1.0).all()


def test_rsi_bounds(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    rsi_df = calculate_rsi(bars, period=14)

    assert "rsi_14" in rsi_df.columns
    assert (rsi_df["rsi_14"] >= 0.0).all()
    assert (rsi_df["rsi_14"] <= 100.0).all()


def test_macd(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    macd_df = calculate_macd(bars)

    assert "macd_line" in macd_df.columns
    assert "macd_signal" in macd_df.columns
    assert "macd_hist" in macd_df.columns
    # Check histogram = line - signal
    np.testing.assert_allclose(macd_df["macd_hist"], macd_df["macd_line"] - macd_df["macd_signal"], rtol=1e-5)


def test_bollinger_bands(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    bb_df = calculate_bollinger_bands(bars)

    assert "bb_upper" in bb_df.columns
    assert "bb_lower" in bb_df.columns
    assert "bb_pct_b" in bb_df.columns
    assert (bb_df["bb_upper"] >= bb_df["bb_lower"]).all()


def test_compute_features_pipeline(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    feat_df = compute_features(bars, mode="full")

    required = ["ret_1", "ret_5", "vol_20", "flow", "flow_5", "log_qty", "rsi_14", "macd_line", "bb_pct_b", "vwap"]
    for col in required:
        assert col in feat_df.columns


def test_legacy_features_compatibility(sample_trades):
    bars = to_bars(sample_trades, sec=1)
    feat_df = features(bars)
    legacy_feats = ["ret_1", "ret_5", "vol_20", "flow", "flow_5", "log_qty"]
    for col in legacy_feats:
        assert col in feat_df.columns
