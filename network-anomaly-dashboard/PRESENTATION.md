# CPU Network Anomaly Detection Dashboard - Presentation

## Slide 1 - Project Title

CPU Network Anomaly Detection Dashboard

Goal: find suspicious network flows, explain them, and map them to MITRE ATT&CK
concepts.

## Slide 2 - Problem

Network-flow logs can be large and hard to inspect manually.

The project helps an analyst answer:

- Which flows are most unusual?
- Why are they unusual?
- What threat behavior could they represent?

## Slide 3 - Architecture

```text
CSV data
  -> preprocessing
  -> Isolation Forest model
  -> anomaly explanation
  -> MITRE ATT&CK mapping
  -> Streamlit dashboard
```

Main files:

- `app.py`
- `preprocessing.py`
- `model.py`
- `explain.py`
- `mitre_mapping.py`

## Slide 4 - Data

The sample dataset contains network-flow style features:

- duration,
- packet counts,
- byte counts,
- packet rate,
- destination port,
- packet size,
- TCP flag counts,
- failed login count.

It includes normal traffic and suspicious examples such as scanning, exfiltration,
flooding-like traffic, and failed-login behavior.

## Slide 5 - Model and Dashboard

The model is Isolation Forest.

Why this model:

- runs on CPU,
- does not need labels,
- works well for an anomaly-detection MVP,
- gives anomaly scores for sorting suspicious rows.

Dashboard sections:

- dataset overview,
- model settings,
- detection metrics,
- suspicious-flow table,
- scatter plot,
- selected anomaly explanation,
- MITRE ATT&CK mapping.

## Slide 6 - MITRE ATT&CK Mapping

The project maps suspicious patterns to ATT&CK hypotheses:

| Pattern | MITRE idea |
| --- | --- |
| Short flow and high packet rate | Active Scanning |
| Extremely high packet rate | Network Denial of Service |
| High outbound byte volume | Exfiltration Over Network |
| Many failed logins | Brute Force |

The mapping is heuristic and supports analyst explanation.

## Slide 7 - Conclusion

The project demonstrates a simple AI cybersecurity workflow:

- load network data,
- detect anomalies,
- explain suspicious rows,
- map findings to MITRE ATT&CK,
- show the result in a dashboard.

Main limitation: the included dataset is small and synthetic.

Next step: test on a larger public dataset such as CICIDS2017 or UNSW-NB15.

## Demo Script

1. Run `streamlit run app.py`.
2. Show the sample dataset loading automatically.
3. Point out row count, column count, and selected numeric features.
4. Show detection metrics and suspicious flows.
5. Select a suspicious row.
6. Show the explanation table.
7. Show the MITRE ATT&CK mapping.
8. Explain that the system is CPU-only and intended as an MVP.
