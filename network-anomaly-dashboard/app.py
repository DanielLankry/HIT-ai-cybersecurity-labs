"""Streamlit dashboard for CPU-based network anomaly detection."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from explain import explain_anomaly
from mitre_mapping import map_to_mitre
from model import run_isolation_forest
from preprocessing import DEFAULT_PREFERRED_FEATURES, preprocess_data


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA_PATH = BASE_DIR / "data" / "sample_network_flows.csv"
IDENTITY_COLUMNS = [
    "Source IP",
    "Src IP",
    "Destination IP",
    "Dst IP",
    "Protocol",
    "Label",
]


def _column_key(column: str) -> str:
    return "".join(character for character in str(column).lower() if character.isalnum())


def _find_existing_column(columns: list[str], candidates: list[str]) -> str | None:
    column_map = {_column_key(column): column for column in columns}
    for candidate in candidates:
        match = column_map.get(_column_key(candidate))
        if match:
            return match
    return None


def _load_dataset(uploaded_file) -> tuple[pd.DataFrame, str]:
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file), uploaded_file.name
    return pd.read_csv(SAMPLE_DATA_PATH), SAMPLE_DATA_PATH.name


def _default_axis(numeric_features: list[str], preferred: str, fallback_index: int) -> str:
    match = _find_existing_column(numeric_features, [preferred])
    if match:
        return match
    return numeric_features[min(fallback_index, len(numeric_features) - 1)]


def _build_anomaly_table(result_df: pd.DataFrame, numeric_features: list[str]) -> pd.DataFrame:
    identity_columns = [
        column for column in result_df.columns if _find_existing_column([column], IDENTITY_COLUMNS)
    ]
    display_columns = (
        identity_columns
        + numeric_features[:12]
        + ["anomaly_score", "prediction_label"]
    )
    display_columns = list(dict.fromkeys(column for column in display_columns if column in result_df.columns))
    return result_df[display_columns].sort_values("anomaly_score", ascending=True)


def main() -> None:
    st.set_page_config(
        page_title="Network Anomaly Detection",
        page_icon=":shield:",
        layout="wide",
    )

    st.title("Network Anomaly Detection Dashboard")
    st.caption("CPU-based Isolation Forest with feature explanations and MITRE ATT&CK heuristics.")

    with st.sidebar:
        st.header("Model Settings")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        contamination = st.slider(
            "Contamination rate",
            min_value=0.01,
            max_value=0.20,
            value=0.02,
            step=0.01,
        )
        n_estimators = st.number_input(
            "Number of estimators",
            min_value=50,
            max_value=500,
            value=100,
            step=50,
        )
        random_state = st.number_input(
            "Random state",
            min_value=0,
            max_value=9999,
            value=42,
            step=1,
        )

    try:
        raw_df, dataset_name = _load_dataset(uploaded_file)
    except Exception as exc:
        st.error(f"Could not load CSV: {exc}")
        st.stop()

    st.subheader("Dataset Overview")
    st.write(f"Loaded dataset: `{dataset_name}`")

    try:
        feature_matrix, cleaned_df, metadata = preprocess_data(
            raw_df,
            preferred_features=DEFAULT_PREFERRED_FEATURES,
        )
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    numeric_features = metadata["numeric_features"]

    overview_cols = st.columns(4)
    overview_cols[0].metric("Rows", f"{metadata['row_count']:,}")
    overview_cols[1].metric("Columns", f"{metadata['column_count']:,}")
    overview_cols[2].metric("Numeric features", f"{len(numeric_features):,}")
    overview_cols[3].metric("Source", "Uploaded" if uploaded_file else "Sample")

    with st.expander("Selected numeric features", expanded=True):
        st.write(", ".join(numeric_features))

    missing_summary = pd.Series(metadata["missing_values"])
    missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
    with st.expander("Missing values in selected numeric features"):
        if missing_summary.empty:
            st.write("No missing or infinite values required imputation.")
        else:
            st.dataframe(
                missing_summary.rename("missing_or_infinite_values"),
                width="stretch",
            )

    st.dataframe(cleaned_df.head(10), width="stretch")

    result_df = run_isolation_forest(
        cleaned_df,
        feature_matrix,
        contamination=contamination,
        n_estimators=int(n_estimators),
        random_state=int(random_state),
    )

    anomalous_count = int((result_df["prediction"] == -1).sum())
    normal_count = int((result_df["prediction"] == 1).sum())
    anomaly_percentage = anomalous_count / len(result_df) * 100

    st.subheader("Detection Results")
    result_cols = st.columns(4)
    result_cols[0].metric("Total flows", f"{len(result_df):,}")
    result_cols[1].metric("Normal flows", f"{normal_count:,}")
    result_cols[2].metric("Anomalous flows", f"{anomalous_count:,}")
    result_cols[3].metric("Anomaly percentage", f"{anomaly_percentage:.2f}%")

    st.subheader("Most Suspicious Flows")
    anomaly_table = _build_anomaly_table(result_df, numeric_features)
    suspicious_rows = anomaly_table.head(50)

    st.dataframe(suspicious_rows, width="stretch", height=320)

    st.subheader("Traffic Visualization")
    x_default = _default_axis(numeric_features, "Flow Duration", 0)
    y_default = _default_axis(numeric_features, "Flow Packets/s", 1)
    axis_cols = st.columns(2)
    x_axis = axis_cols[0].selectbox(
        "X-axis",
        numeric_features,
        index=numeric_features.index(x_default),
    )
    y_axis = axis_cols[1].selectbox(
        "Y-axis",
        numeric_features,
        index=numeric_features.index(y_default),
    )

    hover_columns = [
        column
        for column in result_df.columns
        if column in set(numeric_features[:5] + ["anomaly_score", "prediction_label"])
        or _find_existing_column([column], IDENTITY_COLUMNS)
    ]
    fig = px.scatter(
        result_df,
        x=x_axis,
        y=y_axis,
        color="prediction_label",
        color_discrete_map={"Normal": "#2f855a", "Anomaly": "#c53030"},
        hover_data=hover_columns,
        title=f"{x_axis} vs {y_axis}",
    )
    fig.update_traces(marker={"size": 9, "opacity": 0.78})
    fig.update_layout(legend_title_text="", margin={"l": 20, "r": 20, "t": 50, "b": 20})
    st.plotly_chart(fig, width="stretch")

    st.subheader("Selected Anomaly Explanation")
    if suspicious_rows.empty:
        st.info("No suspicious rows are available for explanation.")
        return

    selected_index = st.selectbox(
        "Selected row index",
        suspicious_rows.index.tolist(),
    )
    selected_row = result_df.loc[selected_index]

    explanation = explain_anomaly(selected_row, result_df, numeric_features, top_n=3)
    st.write(explanation["explanation"])

    if explanation["top_features"]:
        st.dataframe(
            pd.DataFrame(explanation["top_features"]).drop(columns=["unusual_score"]),
            width="stretch",
        )

    st.subheader("MITRE ATT&CK Mapping")
    mappings = map_to_mitre(selected_row, numeric_features, result_df)
    st.dataframe(pd.DataFrame(mappings), width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
