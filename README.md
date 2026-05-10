# ValoRe

## 1. Overview
This repository is associated with the group project for the course **Machine Learning Systems Design (INFO9023-1, 2025–2026)** at ULiège: https://github.com/ThomasVrancken/info9023-mlops

ValoRe is a ML-powered real estate valuation platform. The goal is to build an end-to-end machine learning system that **focuses on system design and engineering components** (data pipelines, cloud infrastructure, CI/CD, reproducibility, deployment) rather than model complexity.


## 2. Project status

### 2.1. Milestone 1 (Sprint 1–2)
**Goal:** set up a clean MLOps foundation with CI/CD and cloud-hosted data for online EDA and baseline training.

Implemented / expected in Milestone 1:
- GitFlow workflow (`main`, `develop`, `feature/*`)
- CI/CD: Ruff + pre-commit + pytest + GitHub Actions on PRs to `develop` and `main`
- Cloud data (online): dataset loaded into **BigQuery** for online EDA and training extraction
- Storage: dataset can also be uploaded to **GCS** (raw CSV + artifacts)
- EDA notebook and first baseline regression experiments
- model training and saved local artifacts

### 2.2. Milestone 2 (Sprint 3–4)

**Goal:** move from a training-focused repository to a more complete ML system by adding model serving, containerization, cloud deployment, and a first cloud training pipeline.


Implemented / expected in Milestone 2:
- migrated dependency management from **pip + requirements.txt** to **uv**
- refactored local modeling code into reusable modules under `src/modeling/`
- added a experimentation notebook to compare candidate regression models
-   selected **XGBRegressor** as the main model family for serving
- built a **API** under `src/api/` with routes
- built a minimal html front-end to display the **HTTP endpoints** and the **Swagger UI** under `src/templates/`
- added a **pytest** assessing the status and output of the **API** under `src/tests/`
- packaged the serving application with **Docker**
- added a first **Vertex AI Pipeline** under `src/vertex/` with components for data ingestion, preprocessing, train/test split, training, evaluation
- used **BigQuery** as the cloud data source and **GCS** for pipeline artifacts
- pushed a dedicated Vertex base image to **Artifact Registry**

### 2.3. Milestone 3 (Sprint 5–6)

The **dashboard/** directory contains the Streamlit frontend for ValoRe, designed for dynamic cloud-based data access rather than static local files. We follow an online (real-time) serving approach: the dashboard sends live requests to the deployed prediction fastAPI for price estimation, while also reading market and model-monitoring data from cloud services (BigQuery, GCS, and Vertex AI Model Registry).
This architecture matches the project requirement that deployed applications must consume cloud data dynamically and demonstrates a complete MLOps serving workflow from user input to cloud model inference and visualization. To consider the amount of concurrent users during the final demo presentation, we set the following parameters on google cloud : limited to 10 concurrent users per container to prevent memory exhaustion and laggy sessions. Horizontal scaling is configured with up to 20 max-instances to support peak loads. Performance tuning includes the allocation of 2 vCPU and 2Gi RAM with no-cpu-throttling to ensure high responsiveness during real-time cloud data fetches. Finally, these requirements were tested using locust (see test/loading).

## 3. Dataset
- Dataset: `Housing.csv` (Kaggle)
- Type: structured/tabular
- Target: house price

The dataset is stored and used **online** via:
- **BigQuery table**: `valore-mlsd-project.valore.housing_raw`
- (Optional) raw file in **GCS**: `gs://mlsd-valore-2026-0001/data/raw/Housing.csv`


## 4. Repository structure

```bash
ValoRe
├── .github/workflows/      # CI/CD pipelines (uv + Docker integration)
├── dashboard/              # Streamlit visualization interface
├── docs/                   # Project documentation & ML Canvas
├── models/                 # Saved local model artifacts and metrics
├── notebooks/              # Exploration, EDA, and experimentation
├── slides/                 # Milestone and presentation decks
├── src/                    # Core source code
│   ├── api/                # API serving layer (FastAPI/Flask)
│   ├── cloud/              # Cloud infrastructure helper functions
│   ├── modeling/           # Training logic and pipeline definitions
│   ├── scripts/            # Utility and standalone execution scripts
│   ├── vertex/             # Vertex AI custom pipeline components
│   └── config.py           # Centralized project configuration
├── templates/              # HTML/UI templates for the API
├── tests/                  # Pytest suite for unit and integration tests and load testing using locust
│
# --- Configuration & Environment ---
├── Dockerfile              # Standard container definition
├── Dockerfile.vertex       # Specialized container for Vertex AI jobs
├── pyproject.toml          # Project metadata and uv dependencies
├── uv.lock                 # Pinning file for deterministic uv installs
├── ruff.toml               # Linting and formatting rules
├── .pre-commit-config.yaml # Automated code quality hooks
└── .python-version         # Targeted Python version for the environment
```


## 5. How we work (GitFlow)

* `main`: milestone-ready only (submission branch)
* `develop`: integration branch
* `feature/*`: development branches


## 6. Contributors

* Antoine DECKERS
* Hoang Linh BUI
* Duy Vu DINH
