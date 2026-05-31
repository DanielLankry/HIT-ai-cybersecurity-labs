# Lab 2 - Anomaly Detection

## Lab Purpose

This lab uses Python to detect suspicious login activity in cybersecurity logs.
The notebook separates normal behavior from likely attack attempts using simple
features such as login hour, failed attempts, session duration, and protocol.

The goal is to practice basic exploratory data analysis and anomaly detection
with a small cybersecurity dataset.

## Main Work

The full pipeline is in:

- `pipeline.ipynb`

The notebook includes:

- loading the dataset
- exploratory data analysis
- feature preparation
- anomaly detection with Isolation Forest
- simple visualizations and evaluation

## Files

- `README.md` - this GitHub folder summary.
- `pipeline.ipynb` - the main notebook for the lab.
- `cybersecurity_logs.csv` - the generated login dataset.
- `synthetic_data_gen.py` - script used to generate the synthetic dataset.

## How To Run

Open `pipeline.ipynb` in Jupyter Notebook or JupyterLab and run the cells from
top to bottom.

The notebook installs/imports the needed Python libraries and reads
`cybersecurity_logs.csv` from the same folder.
