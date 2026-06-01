"""Simple rule-based MITRE ATT&CK mapping for suspicious network-flow patterns."""

from __future__ import annotations

import re

import pandas as pd


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _find_column(columns: list[str], candidates: list[str]) -> str | None:
    column_keys = {_key(column): column for column in columns}
    for candidate in candidates:
        direct = column_keys.get(_key(candidate))
        if direct:
            return direct

    candidate_keys = [_key(candidate) for candidate in candidates]
    for column in columns:
        column_key = _key(column)
        if any(candidate_key in column_key for candidate_key in candidate_keys):
            return column
    return None


def _value(row: pd.Series, column: str | None) -> float | None:
    if not column:
        return None
    value = row.get(column)
    if pd.isna(value):
        return None
    return float(value)


def _median(reference_df: pd.DataFrame, column: str | None) -> float | None:
    if not column:
        return None
    value = reference_df[column].median()
    if pd.isna(value):
        return None
    return float(value)


def _is_high(value: float | None, median: float | None, multiplier: float) -> bool:
    if value is None or median is None:
        return False
    baseline = abs(median) if abs(median) > 1e-9 else 1.0
    return value > baseline * multiplier


def _is_short(value: float | None, median: float | None) -> bool:
    if value is None or median is None:
        return False
    return value < max(median * 0.5, 1.0)


def map_to_mitre(
    row: pd.Series,
    numeric_features: list[str],
    reference_df: pd.DataFrame,
) -> list[dict]:
    """Map suspicious numeric patterns to readable MITRE ATT&CK hypotheses."""
    mappings: list[dict] = []

    duration_col = _find_column(numeric_features, ["Flow Duration", "Duration"])
    packet_rate_col = _find_column(
        numeric_features,
        ["Flow Packets/s", "Packets/s", "Packet Rate", "Packets Per Second"],
    )
    outbound_bytes_col = _find_column(
        numeric_features,
        [
            "Total Length of Fwd Packets",
            "Total Fwd Bytes",
            "Outbound Bytes",
            "Fwd Packet Length Total",
        ],
    )

    duration = _value(row, duration_col)
    duration_median = _median(reference_df, duration_col)
    packet_rate = _value(row, packet_rate_col)
    packet_rate_median = _median(reference_df, packet_rate_col)
    outbound_bytes = _value(row, outbound_bytes_col)
    outbound_bytes_median = _median(reference_df, outbound_bytes_col)

    if _is_short(duration, duration_median) and _is_high(packet_rate, packet_rate_median, 5):
        mappings.append(
            {
                "possible_behavior": "Scanning or rapid probing",
                "tactic": "Reconnaissance",
                "technique": "Active Scanning",
                "reasoning": (
                    "The flow is much shorter than typical traffic while packet rate "
                    "is much higher than the dataset median."
                ),
            }
        )

    if _is_short(duration, duration_median) and _is_high(packet_rate, packet_rate_median, 20):
        mappings.append(
            {
                "possible_behavior": "Flooding or service disruption",
                "tactic": "Impact",
                "technique": "Network Denial of Service",
                "reasoning": (
                    "Extremely high packets per second in a short flow can indicate "
                    "traffic flooding behavior."
                ),
            }
        )

    if _is_high(outbound_bytes, outbound_bytes_median, 10):
        mappings.append(
            {
                "possible_behavior": "Large outbound transfer",
                "tactic": "Exfiltration",
                "technique": "Exfiltration Over Network",
                "reasoning": (
                    "Outbound byte volume is far above the dataset median, which can "
                    "match data movement or exfiltration behavior."
                ),
            }
        )

    failed_login_col = _find_column(
        numeric_features,
        [
            "Failed Logins",
            "Failed Login Count",
            "Login Failures",
            "Failed Attempts",
            "Authentication Failures",
            "Wrong Password Count",
        ],
    )
    failed_login_value = _value(row, failed_login_col)
    failed_login_median = _median(reference_df, failed_login_col)
    if _is_high(failed_login_value, failed_login_median, 5):
        mappings.append(
            {
                "possible_behavior": "Repeated failed authentication",
                "tactic": "Credential Access",
                "technique": "Brute Force",
                "reasoning": (
                    "Failed-login-like fields are much higher than the dataset median."
                ),
            }
        )

    if not mappings:
        mappings.append(
            {
                "possible_behavior": "No strong MITRE heuristic matched",
                "tactic": "Unknown",
                "technique": "Needs analyst review",
                "reasoning": (
                    "The row is anomalous according to the model, but the simple MVP "
                    "rules did not match a specific behavior."
                ),
            }
        )

    return mappings
