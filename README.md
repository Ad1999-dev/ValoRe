# ValoRe

## Milestone 1 (Sprint 1–2) status
**Goal:** set up a clean MLOps foundation with CI/CD and cloud-hosted data for online EDA and baseline training.

Implemented / expected in Milestone 1:
- GitFlow workflow (`main`, `develop`, `feature/*`)
- CI/CD: Ruff + pre-commit + pytest + GitHub Actions on PRs to `develop` and `main`
- Cloud data (online): dataset loaded into **BigQuery** for online EDA and training extraction
- Storage: dataset can also be uploaded to **GCS** (raw CSV + future artifacts)

Key docs:
- `docs/README.md` (documentation index)
- `docs/cloud_initialization.md` (how to run cloud ingestion & checks)
- `docs/gcp_config.md` (project resources: IAM / BigQuery / GCS)

---

## Overview
This repository is associated with the group project for the course **Machine Learning Systems Design (INFO9023-1, 2025–2026)** at ULiège: https://github.com/ThomasVrancken/info9023-mlops

ValoRe is a ML-powered real estate valuation platform. The goal is to build an end-to-end machine learning system that **focuses on system design and engineering components** (data pipelines, cloud infrastructure, CI/CD, reproducibility, deployment) rather than model complexity.

---

## Dataset
- Dataset: `Housing.csv` (Kaggle: Housing Price Dataset)
- Type: structured/tabular
- Target: house price (exact column name confirmed in EDA)

**Important:** the dataset is **not committed to Git**.
For Milestone 1, the dataset is stored and used **online** via:
- **BigQuery table**: `valore-mlsd-project.valore.housing_raw`
- (Optional) raw file in **GCS**: `gs://mlsd-valore-2026-0001/data/raw/Housing.csv`

---

## Quick start (Milestone 1)
All commands below should be run from the repository root.

### 1) Authenticate to Google Cloud
```bash
gcloud init
gcloud config set project valore-mlsd-project
gcloud auth application-default login
```

### 2) Load dataset into BigQuery (online source)

Edit config values inside:

* `src/scripts/load_housing_to_bigquery.py`

Run:

```bash
python -m src.scripts.load_housing_to_bigquery
```

### 3) Verify online queries

Edit config values (and confirm target column name) inside:

* `src/scripts/check_bigquery_queries.py`

Run:

```bash
python -m src.scripts.check_bigquery_queries
```

### Upload raw dataset to GCS

Edit config values inside:

* `src/scripts/gcs_setup_and_upload.py`

Run:

```bash
python -m src.scripts.gcs_setup_and_upload
```

---

## Repository structure

```
ValoRe
├── src/                        # source code (cloud utilities + scripts)
├── tests/                      # pytest tests
├── docs/                       # documentation (dataset card, data dictionary, cloud setup, etc.)
├── notebooks/                  # EDA notebooks
└── slides/                     # milestone slides (must be committed for grading)
```

---

## How we work (GitFlow)

* `main`: milestone-ready only (submission branch)
* `develop`: integration branch
* `feature/*`: development branches

---

## Contributors

* Antoine DECKERS
* Hoang Linh BUI
* Duy Vu DINH
