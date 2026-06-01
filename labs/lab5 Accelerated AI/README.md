# Lab 5 - Accelerated AI

In this lab I built a small event-driven cybersecurity pipeline. The pipeline
uses Kafka for passing events, Jupyter notebooks for the lab work, Redpanda
Console for checking Kafka messages, and Jaeger for tracing.

The flow is:

```text
Producer notebook
  -> Kafka topic: raw-events
  -> Consumer and MITRE classifier notebook
  -> classified_packets.csv
  -> Statistics notebook
```

## Requirement Check

| Requirement | Where I did it |
| --- | --- |
| Run the lab with Docker Compose | `compose.yml` |
| Use Kafka as the event broker | `kafka` service and topic `raw-events` |
| Produce cybersecurity events | `notebooks/mitre_classification/1_Producer.ipynb` |
| Consume and classify events | `notebooks/mitre_classification/2_Consumer_Classifier.ipynb` |
| Map events to MITRE ATT&CK | classifier rules for PowerShell, cmd, failed login, and valid login |
| Save classified output | `notebooks/mitre_classification/classified_packets.csv` |
| Show statistics and charts | `notebooks/mitre_classification/3_Statistics.ipynb` |
| Use a UI to inspect Kafka | Redpanda Console on `http://localhost:8082` |
| Use tracing | Jaeger on `http://localhost:16686` with producer and classifier spans |

## Files

- `compose.yml` - starts Kafka, Redpanda Console, Jaeger, and JupyterLab.
- `.gitignore` - ignores notebook checkpoints and Python cache files.
- `notebooks/mitre_classification/1_Producer.ipynb` - creates fake Windows-like events and sends them to Kafka.
- `notebooks/mitre_classification/2_Consumer_Classifier.ipynb` - reads events from Kafka and classifies them.
- `notebooks/mitre_classification/3_Statistics.ipynb` - reads the CSV and shows counts/charts.
- `notebooks/mitre_classification/classified_packets.csv` - example output from a completed run.

## How To Run

From this folder:

```powershell
docker compose up --build
```

Open:

- JupyterLab: `http://localhost:8888`
- Redpanda Console: `http://localhost:8082`
- Jaeger: `http://localhost:16686`

Run the notebooks in this order:

1. `1_Producer.ipynb`
2. `2_Consumer_Classifier.ipynb`
3. `3_Statistics.ipynb`

## What The Notebooks Do

The producer creates 30 simple security events. The events are either process
starts or user logins. Some process events look like PowerShell or cmd activity,
and some login events are successful or failed logins.

The consumer reads from Kafka and maps each event to a MITRE ATT&CK tactic and
technique:

| Event | MITRE mapping |
| --- | --- |
| PowerShell encoded command | `TA0002 / T1059.001` |
| `cmd.exe` execution | `TA0002 / T1059.003` |
| Other command execution | `TA0002 / T1059` |
| Failed login | `TA0006 / T1110` |
| Successful login | `TA0001 / T1078` |

The statistics notebook loads the CSV output and shows:

- total classified events
- event counts by type
- counts by MITRE tactic
- counts by MITRE technique
- simple charts

## Questions

### Why use Kafka instead of direct function calls?

Kafka separates the producer from the consumer. The producer can send events
without needing the classifier to run at the exact same time.

### What happens if the consumer is slower than the producer?

The events stay in Kafka until the consumer reads them. This helps prevent the
pipeline from immediately losing events.

### How does tracing help?

Tracing shows which stage handled each event. In this lab it helps check the
producer and classifier flow in Jaeger.

### Which stages could be scaled independently?

The producer and classifier could be scaled separately because Kafka is between
them. The statistics part is also separate because it only reads the CSV output.

### How would this change in a real SOC?

In a real SOC the events would come from real logs, the classifier rules would
be stronger, the results would probably go into a SIEM or database, and the
dashboards would be used for monitoring.
