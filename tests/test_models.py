"""Tests for machine learning models, labeling, and metrics."""
import numpy as np
import pandas as pd
import pytest

from quantpulse.data.synthetic import generate_synthetic_trades
from quantpulse.features.aggregator import to_bars
from quantpulse.features.pipeline import compute_features
from quantpulse.models.labeler import create_labels
from quantpulse.models.metrics import evaluate_classification
from quantpulse.models.registry import get_models
from quantpulse.models.trainer import ModelTrainer, train


@pytest.fixture
def feature_bars():
    trades = generate_synthetic_trades(n_trades=5000, seed=42)
    bars = to_bars(trades, sec=1)
    return compute_features(bars, mode="full").dropna(subset=["ret_1", "ret_5", "vol_20", "flow", "flow_5", "log_qty"])


def test_create_labels(feature_bars):
    labeled, lo, hi = create_labels(feature_bars, ahead=10, tail=0.25)
    assert "future" in labeled.columns
    assert "label" in labeled.columns
    assert lo < hi
    labels = set(labeled["label"].dropna().unique())
    assert labels.issubset({0, 1, 2})


def test_evaluate_classification():
    y_true = np.array([0, 1, 2, 1, 0, 2, 1, 1, 1, 0])
    y_pred = np.array([0, 1, 2, 1, 0, 1, 1, 1, 2, 0])
    metrics = evaluate_classification(y_true, y_pred)

    assert "accuracy" in metrics
    assert "baseline_accuracy" in metrics
    assert "balanced_accuracy" in metrics
    assert "f1_macro" in metrics
    assert "confusion_matrix" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0


def test_get_models():
    models = get_models()
    assert "Random Forest" in models
    assert "Gradient Boosting" in models
    assert "Logistic Regression" in models
    assert "Decision Tree" in models


def test_model_trainer_walk_forward(feature_bars):
    models = get_models()
    rf = models["Random Forest"]
    res = ModelTrainer.train(feature_bars, rf, ahead=10, tail=0.25, test_ratio=0.30)

    assert res.accuracy > 0.0
    assert res.baseline > 0.0
    assert res.test_data is not None
    assert len(res.y_pred) == len(res.y_true)
    assert res.feature_importance is not None


def test_legacy_train_tuple_unpacking(feature_bars):
    models = get_models()
    dt = models["Decision Tree"]
    acc, base = train(feature_bars, dt)

    assert isinstance(acc, float)
    assert isinstance(base, float)
    assert 0.0 <= acc <= 1.0
    assert 0.0 <= base <= 1.0
