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
- packaged the serving application with **Docker**
- added a first **Vertex AI Pipeline** under `src/vertex/` with components for data ingestion, preprocessing, train/test split, training, evaluation
- used **BigQuery** as the cloud data source and **GCS** for pipeline artifacts
- pushed a dedicated Vertex base image to **Artifact Registry**

### 2.3. Milestone 3 (Sprint 5–6)
(TBD)



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
├── src/                              # source code
│   ├── config.py                     # project configuration
│   ├── api/                          # API serving layer
│   ├── cloud/                        # cloud helper functions
│   ├── modeling/                     # local training code
│   ├── scripts/                      # utility scripts
│   └── vertex/                       # Vertex AI pipeline code
├── template/                         # template files for API
├── tests/                            # pytest tests
├── models/                           # saved local model artifacts and metrics
├── docs/                             # project documentation
├── notebooks/                        # notebooks used during exploration and experimentation
│   ├── eda.ipynb                     # exploratory data analysis
│   └── experimentation.ipynb         # model comparison notebook used to choose the serving model family
└── slides/                           # milestone slides
```


## 5. How we work (GitFlow)

* `main`: milestone-ready only (submission branch)
* `develop`: integration branch
* `feature/*`: development branches


## 6. Contributors

* Antoine DECKERS
* Hoang Linh BUI
* Duy Vu DINH
