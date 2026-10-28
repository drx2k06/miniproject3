"""Model factory and registry for quantitative crypto classifiers."""
from __future__ import annotations

from typing import Any, Dict

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None


def get_models(random_state: int = 42) -> Dict[str, Any]:
    """Return dictionary of configured classifiers for crypto signal generation."""
    models: Dict[str, Any] = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=6,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            random_state=random_state,
        ),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                class_weight="balanced",
                max_iter=500,
                random_state=random_state,
            )),
        ]),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5,
            class_weight="balanced",
            random_state=random_state,
        ),
    }

    if XGBClassifier is not None:
        models["XGBoost"] = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            random_state=random_state,
            eval_metric="mlogloss",
        )

    return models
