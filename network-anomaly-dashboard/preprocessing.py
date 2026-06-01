"""Data preparation helpers for network-flow anomaly detection."""

from __future__ import annotations

import re
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


DEFAULT_PREFERRED_FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Destination Port",
    "Packet Length Mean",
    "Average Packet Size",
    "SYN Flag Count",
    "ACK Flag Count",
]


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with lightly normalized, readable column names."""
    cleaned = df.copy()
    cleaned.columns = [
        re.sub(r"\s+", " ", str(column).replace("_", " ")).strip()
        for column in cleaned.columns
    ]
    return cleaned


def _column_key(column: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(column).lower())


def get_numeric_features(
    df: pd.DataFrame,
    preferred_features: Iterable[str] | None = None,
) -> list[str]:
    """Select numeric features, prioritizing common network-flow columns."""
    preferred_features = list(preferred_features or DEFAULT_PREFERRED_FEATURES)
    numeric_columns = list(df.select_dtypes(include=[np.number]).columns)
    numeric_keys = {_column_key(column): column for column in numeric_columns}

    selected: list[str] = []
    for feature in preferred_features:
        matching_column = numeric_keys.get(_column_key(feature))
        if matching_column and matching_column not in selected:
            selected.append(matching_column)

    for column in numeric_columns:
        if column not in selected:
            selected.append(column)

    return selected


def preprocess_data(
    df: pd.DataFrame,
    preferred_features: Iterable[str] | None = None,
) -> tuple[np.ndarray, pd.DataFrame, dict]:
    """Clean, impute, and scale numeric network-flow features."""
    if df.empty:
        raise ValueError("The dataset is empty. Upload a CSV with network-flow rows.")

    cleaned_df = clean_column_names(df)
    numeric_features = get_numeric_features(cleaned_df, preferred_features)

    if len(numeric_features) < 2:
        raise ValueError(
            "At least two numeric network-flow features are required for detection "
            "and visualization."
        )

    numeric_data = cleaned_df[numeric_features].replace([np.inf, -np.inf], np.nan)
    missing_values_before = numeric_data.isna().sum().to_dict()

    medians = numeric_data.median(numeric_only=True)
    numeric_data = numeric_data.fillna(medians).fillna(0)
    cleaned_df[numeric_features] = numeric_data

    scaler = StandardScaler()
    feature_matrix = scaler.fit_transform(numeric_data)

    metadata = {
        "numeric_features": numeric_features,
        "missing_values": missing_values_before,
        "scaler": scaler,
        "row_count": len(cleaned_df),
        "column_count": len(cleaned_df.columns),
    }

    return feature_matrix, cleaned_df, metadata
