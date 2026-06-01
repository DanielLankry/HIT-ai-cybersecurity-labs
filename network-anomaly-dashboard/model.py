"""CPU-based anomaly detection model utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def run_isolation_forest(
    df: pd.DataFrame,
    feature_matrix,
    contamination: float = 0.02,
    n_estimators: int = 100,
    random_state: int = 42,
) -> pd.DataFrame:
    """Train Isolation Forest and attach predictions to the original rows."""
    if len(df) != len(feature_matrix):
        raise ValueError("Feature matrix row count must match the dataframe row count.")

    model = IsolationForest(
        contamination=contamination,
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
    )
    predictions = model.fit_predict(feature_matrix)
    scores = model.decision_function(feature_matrix)

    result = df.copy()
    result["prediction"] = predictions
    result["prediction_label"] = np.where(predictions == -1, "Anomaly", "Normal")
    result["anomaly_score"] = scores
    return result
