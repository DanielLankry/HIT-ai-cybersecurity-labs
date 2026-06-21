# HIT AI Cybersecurity Labs and Project

This repository contains the course lab submissions and the final project for
Introduction to AI-Driven Cybersecurity.

## Repository Structure

| Folder | Content | Status |
| --- | --- | --- |
| `labs/lab1 Cyber Threat Intelligence` | Storm-2755 CTI report mapped to MITRE ATT&CK | Complete |
| `labs/lab2 Anomaly Detection` | Synthetic login dataset, EDA, and Isolation Forest notebook | Complete |
| `labs/lab3 Agent` | Password strength checker agent with Chainlit | Complete |
| `labs/lab4 MAF LLM Agent Workflow` | Safe query rewriter workflow with Microsoft Agent Framework | Complete |
| `labs/lab5 Accelerated AI` | Kafka event pipeline, MITRE classifier, tracing, and statistics notebooks | Complete |
| `network-anomaly-dashboard` | Final project: CPU network anomaly detection dashboard | Complete MVP |

## Final Project

The final project is in `network-anomaly-dashboard`.

It implements a CPU-only Streamlit dashboard that:

- loads network-flow CSV data,
- preprocesses numeric traffic features,
- detects anomalous flows with Isolation Forest,
- explains suspicious rows with simple feature comparisons,
- maps suspicious behavior to MITRE ATT&CK hypotheses,
- presents the result in an interactive dashboard.

Project deliverables:

- `network-anomaly-dashboard/README.md` - setup and project overview.
- `network-anomaly-dashboard/REPORT.md` - written project report.
- `network-anomaly-dashboard/PRESENTATION.md` - short presentation and demo outline.
- `network-anomaly-dashboard/screenshots/dashboard-overview.png` - dashboard screenshot.

## How To Run

### Lab 3

```powershell
cd "labs\lab3 Agent"
Copy-Item .env.template .env
# edit .env and put your API key
docker compose up --build
```

Open `http://localhost:8000`.

### Lab 4

```powershell
cd "labs\lab4 MAF LLM Agent Workflow"
Copy-Item .env.template .env
# edit .env and put your API key
docker compose up --build
```

Open `http://localhost:8081`.

### Lab 5

```powershell
cd "labs\lab5 Accelerated AI"
docker compose up --build
```

Open:

- JupyterLab: `http://localhost:8888`
- Redpanda Console: `http://localhost:8082`
- Jaeger: `http://localhost:16686`

### Final Project

```powershell
cd network-anomaly-dashboard
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard starts with the sample CSV if no custom file is uploaded.

## Security Note

Real API keys must stay only in local `.env` files. Do not commit `.env` files
or paste keys into `compose.yml`, notebooks, or Markdown files.

If an API key was ever committed or shared publicly, revoke it in the provider
dashboard and create a new key.

## Submission Checklist

- Labs 1-5 are present in `labs/`.
- Each lab has a folder-level `README.md` for GitHub readability.
- The final project is a repo-root folder, not inside `labs/`.
- The final project includes code, sample data, tests, screenshot, report, and
  presentation notes.
- Local secrets are ignored and represented only by `.env.template` files.
