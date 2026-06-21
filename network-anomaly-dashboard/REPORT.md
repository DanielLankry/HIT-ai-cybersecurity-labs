# CPU Network Anomaly Detection Dashboard - Project Report

## Problem Statement

Security teams need a fast way to review network-flow logs and find suspicious
traffic. Raw CSV logs can contain many rows and numeric features, so manual
inspection is slow. The goal of this project is to build a simple local
dashboard that detects unusual network flows, explains why a row looks unusual,
and connects the suspicious behavior to MITRE ATT&CK concepts.

## Project Type

This is an integrated project. It combines:

- machine learning for anomaly detection,
- network traffic data analysis,
- feature-based explanations,
- MITRE ATT&CK mapping,
- dashboard visualization for analyst review.

## Architecture

```text
CSV file or sample dataset
  -> preprocessing.py
  -> model.py Isolation Forest
  -> explain.py feature explanation
  -> mitre_mapping.py ATT&CK heuristic mapping
  -> app.py Streamlit dashboard
```

The implementation is split into small modules so each part is easy to test and
explain:

- `app.py` controls the Streamlit user interface.
- `preprocessing.py` selects numeric features and cleans missing or infinite values.
- `model.py` runs the CPU Isolation Forest model.
- `explain.py` compares suspicious rows to dataset medians.
- `mitre_mapping.py` maps suspicious patterns to readable ATT&CK hypotheses.

## Chosen Technologies

| Technology | Use |
| --- | --- |
| Python | Main programming language |
| Streamlit | Interactive dashboard |
| pandas and numpy | Data loading and preprocessing |
| scikit-learn | Isolation Forest anomaly detection |
| Plotly | Scatter plot visualization |
| pytest/unittest | Core behavior testing |

The project intentionally stays CPU-only. It does not require GPU acceleration,
CUDA, RAPIDS, Morpheus, Triton, or NVIDIA hardware.

## Dataset and Data Analysis

The included sample dataset is synthetic but shaped like common network-flow
CSV data. It contains 24 rows and features such as:

- flow duration,
- forward and backward packet counts,
- byte counts,
- packet rate,
- destination port,
- packet size,
- SYN and ACK flag counts,
- failed login count.

Most rows represent normal web or DNS traffic. A small number of rows represent
clear suspicious patterns:

- rapid SSH-style probing,
- high packet-rate traffic,
- large outbound transfer,
- flooding-like UDP traffic,
- repeated failed-login behavior.

The dashboard first shows dataset size, selected numeric features, missing-value
handling, and a preview. This gives the analyst context before trusting the
model output.

## Model and Results

The MVP uses `sklearn.ensemble.IsolationForest`.

Reasons for choosing it:

- it works without labeled data,
- it is simple to run on CPU,
- it is appropriate for a small anomaly-detection MVP,
- it returns an anomaly score that can be sorted and reviewed.

The dashboard displays:

- total flows,
- normal flow count,
- anomalous flow count,
- anomaly percentage,
- top suspicious rows sorted by anomaly score,
- a scatter plot comparing two selected features.

The model result is not treated as proof of malicious behavior. It is used as a
triage signal that tells the analyst which rows deserve review first.

## Explanation Method

For a selected anomalous row, the project compares the row's numeric values to
the dataset median. The dashboard then shows which features are most unusual.

This is intentionally simple and readable. For example, if packet rate is much
higher than the median and duration is very short, the analyst can understand
why the row may look like scanning or flooding behavior.

## MITRE ATT&CK Mapping

The project uses simple heuristic rules to map suspicious network behavior to
MITRE ATT&CK ideas:

| Suspicious pattern | Tactic | Technique |
| --- | --- | --- |
| Short duration and high packet rate | Reconnaissance | Active Scanning |
| Extremely high packet rate in a short flow | Impact | Network Denial of Service |
| Very high outbound byte volume | Exfiltration | Exfiltration Over Network |
| Repeated failed authentication | Credential Access | Brute Force |

This mapping is not formal attribution. It is a helpful explanation layer for a
student project and for analyst triage.

## Conclusions

The project meets the main course requirements for an AI cybersecurity defense
system MVP:

- it has a clear cybersecurity problem,
- it uses AI/ML to detect suspicious behavior,
- it analyzes network-flow data,
- it presents results visually,
- it explains detections,
- it uses MITRE ATT&CK to describe possible threat behavior,
- it runs locally without GPU acceleration.

The strongest part of the project is that it connects model output to analyst
review instead of only printing predictions. The main limitation is that the
sample dataset is small and synthetic, so the dashboard should be treated as a
prototype rather than a production SOC system.

## Future Work

- Evaluate with a larger public dataset such as CICIDS2017 or UNSW-NB15.
- Add categorical feature encoding for protocol and IP-based features.
- Add downloadable results.
- Add richer MITRE rules.
- Compare Isolation Forest with another model such as Local Outlier Factor or
  One-Class SVM.
