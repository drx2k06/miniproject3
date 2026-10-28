"""Walk-forward time-series training and model evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from quantpulse.config import default_config
from quantpulse.models.labeler import create_labels
from quantpulse.models.metrics import evaluate_classification


@dataclass
class TrainResult:
    """Rich training result container supporting tuple unpacking for legacy compatibility."""

    accuracy: float
    baseline: float
    model: Any
    metrics: Dict[str, Any]
    feature_names: List[str]
    feature_importance: Optional[Dict[str, float]]
    test_data: pd.DataFrame
    y_true: np.ndarray
    y_pred: np.ndarray
    y_prob: Optional[np.ndarray]

    def __iter__(self):
        """Allow backward-compatible unpacking: acc, base = train(...)"""
        yield self.accuracy
        yield self.baseline

    def __getitem__(self, item):
        if item == 0:
            return self.accuracy
        elif item == 1:
            return self.baseline
        raise IndexError("TrainResult legacy index must be 0 (accuracy) or 1 (baseline)")


class ModelTrainer:
    """Walk-forward time-series model trainer."""

    @classmethod
    def train(
        cls,
        bars: pd.DataFrame,
        model: Any,
        features: Optional[List[str]] = None,
        ahead: int = 10,
        tail: float = 0.25,
        test_ratio: float = 0.30,
    ) -> TrainResult:
        """Fit model on chronological training window and evaluate on forward test window."""
        b = bars.copy()
        labeled_b, lo, hi = create_labels(b, ahead=ahead, tail=tail)

        # Select features present in dataframe
        if features is None:
            available_full = [f for f in default_config.full_features if f in labeled_b.columns]
            if len(available_full) >= 4:
                selected_features = available_full
            else:
                selected_features = [f for f in default_config.baseline_features if f in labeled_b.columns]
        else:
            selected_features = [f for f in features if f in labeled_b.columns]

        if not selected_features:
            raise ValueError("No valid feature columns found in dataset.")

        clean_data = labeled_b.dropna(subset=selected_features + ["future", "label"]).copy()
        if len(clean_data) < 20:
            raise ValueError(f"Insufficient samples ({len(clean_data)}) after feature nan-drop.")

        # Chronological time-series split (past -> train, future -> test)
        cut = int(len(clean_data) * (1.0 - test_ratio))
        train_df = clean_data.iloc[:cut]
        test_df = clean_data.iloc[cut:].copy()

        X_tr = train_df[selected_features]
        y_tr = train_df["label"].astype(int)

        X_te = test_df[selected_features]
        y_te = test_df["label"].astype(int)

        # Fit model
        model.fit(X_tr, y_tr)

        # Predict
        y_pred = model.predict(X_te)
        y_prob = None
        if hasattr(model, "predict_proba"):
            try:
                y_prob = model.predict_proba(X_te)
            except Exception:
                pass

        test_df["prediction"] = y_pred

        # Metrics
        metrics = evaluate_classification(y_te, y_pred, y_prob)

        # Feature importances
        importance_dict = None
        estimator = model
        if hasattr(model, "named_steps") and "clf" in model.named_steps:
            estimator = model.named_steps["clf"]

        if hasattr(estimator, "feature_importances_"):
            importances = estimator.feature_importances_
            importance_dict = {
                name: float(val)
                for name, val in sorted(
                    zip(selected_features, importances),
                    key=lambda x: x[1],
                    reverse=True,
                )
            }
        elif hasattr(estimator, "coef_"):
            coef = np.mean(np.abs(estimator.coef_), axis=0)
            importance_dict = {
                name: float(val)
                for name, val in sorted(
                    zip(selected_features, coef),
                    key=lambda x: x[1],
                    reverse=True,
                )
            }

        return TrainResult(
            accuracy=metrics["accuracy"],
            baseline=metrics["baseline_accuracy"],
            model=model,
            metrics=metrics,
            feature_names=selected_features,
            feature_importance=importance_dict,
            test_data=test_df,
            y_true=y_te.values,
            y_pred=y_pred,
            y_prob=y_prob,
        )


def train(
    b: pd.DataFrame,
    model: Any,
    features: Optional[List[str]] = None,
    ahead: int = 10,
    tail: float = 0.25,
    test: float = 0.30,
) -> TrainResult:
    """Convenience wrapper matching legacy API signature."""
    return ModelTrainer.train(
        bars=b,
        model=model,
        features=features,
        ahead=ahead,
        tail=tail,
        test_ratio=test,
    )
