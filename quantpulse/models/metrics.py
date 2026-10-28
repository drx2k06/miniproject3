"""Comprehensive multi-class classification and risk metrics."""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_classification(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray | pd.Series,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Calculate multi-class classification performance metrics.

    Evaluates beyond raw accuracy to guard against misleading majority-class guessing.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    # Baseline majority class accuracy
    unique_classes, counts = np.unique(y_true, return_counts=True)
    baseline_acc = float(np.max(counts) / len(y_true)) if len(y_true) > 0 else 0.0

    # Model metrics
    acc = float(accuracy_score(y_true, y_pred))
    balanced_acc = float(balanced_accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
    cm_norm = cm.astype(float) / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)

    return {
        "accuracy": acc,
        "baseline_accuracy": baseline_acc,
        "beats_baseline": acc > baseline_acc,
        "accuracy_edge": acc - baseline_acc,
        "balanced_accuracy": balanced_acc,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_norm": cm_norm.tolist(),
        "class_distribution": {int(k): int(v) for k, v in zip(unique_classes, counts)},
    }
