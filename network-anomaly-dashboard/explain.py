"""Feature-based explanations for selected anomalous network flows."""

from __future__ import annotations

import math

import pandas as pd


def _format_value(value) -> str:
    if pd.isna(value):
        return "missing"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return f"{value:,}" if isinstance(value, int) else str(value)


def explain_anomaly(
    row: pd.Series,
    reference_df: pd.DataFrame,
    numeric_features: list[str],
    top_n: int = 3,
) -> dict:
    """Explain one row by comparing its numeric values to dataset medians."""
    if not numeric_features:
        return {
            "top_features": [],
            "explanation": "No numeric features are available for explanation.",
        }

    medians = reference_df[numeric_features].median(numeric_only=True)
    unusual_features = []

    for feature in numeric_features:
        value = row.get(feature)
        median = medians.get(feature)
        if pd.isna(value) or pd.isna(median):
            continue

        denominator = abs(float(median)) if abs(float(median)) > 1e-9 else 1.0
        unusual_score = abs(float(value) - float(median)) / denominator
        direction = "higher than" if float(value) > float(median) else "lower than"

        unusual_features.append(
            {
                "feature": feature,
                "value": value,
                "median": median,
                "direction": direction,
                "unusual_score": unusual_score,
            }
        )

    unusual_features.sort(key=lambda item: item["unusual_score"], reverse=True)
    top_features = unusual_features[:top_n]

    row_label = row.get("prediction_label", "Anomaly")
    review_phrase = "was marked anomalous" if row_label == "Anomaly" else "was selected for review"

    if top_features:
        reasons = [
            (
                f"{item['feature']} is {item['direction']} the dataset median "
                f"({_format_value(item['value'])} vs {_format_value(item['median'])})"
            )
            for item in top_features
        ]
        explanation = f"Flow {row.name} {review_phrase} because " + ", ".join(reasons) + "."
    else:
        explanation = (
            f"Flow {row.name} {review_phrase}, but the selected numeric features "
            "do not differ strongly from dataset medians."
        )

    anomaly_score = row.get("anomaly_score")
    if anomaly_score is not None and not (isinstance(anomaly_score, float) and math.isnan(anomaly_score)):
        explanation += f" Its anomaly score is {_format_value(float(anomaly_score))}."

    return {
        "top_features": top_features,
        "explanation": explanation,
    }
