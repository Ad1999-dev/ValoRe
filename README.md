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


### 2.2. Milestone 2 (Sprint 3–4)
(TBD)

### 2.3. Milestone 3 (Sprint 5–6)
(TBD)



## 3. Dataset
- Dataset: `Housing.csv` (Kaggle: Housing Price Dataset)
- Type: structured/tabular
- Target: house price (exact column name confirmed in EDA)

**Important:** the dataset is **not committed to Git**.
For Milestone 1, the dataset is stored and used **online** via:
- **BigQuery table**: `valore-mlsd-project.valore.housing_raw`
- (Optional) raw file in **GCS**: `gs://mlsd-valore-2026-0001/data/raw/Housing.csv`


## 4. Repository structure

```
ValoRe
├── src/                        # source code
├── tests/                      # pytest tests
├── models/                     # saved models
├── docs/                       # documentation
├── notebooks/                  # notebooks
└── slides/                     # milestone slides
```


## 5. How we work (GitFlow)

* `main`: milestone-ready only (submission branch)
* `develop`: integration branch
* `feature/*`: development branches


## 6. Contributors

* Antoine DECKERS
* Hoang Linh BUI
* Duy Vu DINH
