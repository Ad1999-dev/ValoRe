# SETUP

## 1. Python environment

Create a fresh environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Google Cloud login

We use Google Cloud because the course expects cloud-based storage instead of only local files.

Run:

```bash
gcloud init
gcloud config set project valore-mlsd-project
gcloud auth application-default login
```

If needed, fix the quota project:

```bash
gcloud auth application-default set-quota-project valore-mlsd-project
```

## 3. APIs we use

For milestone 1, the important services are:

* BigQuery
* Cloud Storage

If they are not enabled yet:

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

## 4. Current project values

These are the values used in the repo right now:

* Project ID: `valore-mlsd-project`
* Region: `europe-west1`
* BigQuery dataset: `valore`
* BigQuery table: `housing_raw`
* GCS bucket: `mlsd-valore-2026-0001`
* GCS raw file path: `data/raw/Housing.csv`

These values are now also stored centrally in `src/config.py`.

## 5. Useful scripts

### Upload raw CSV to GCS

```bash
python -m src.scripts.gcs_setup_and_upload
```

### Load the dataset into BigQuery

```bash
python -m src.scripts.load_housing_to_bigquery
```

### Check that the BigQuery table works

```bash
python -m src.scripts.check_bigquery_queries
```

## 6. Rerun the current baseline model

This is the most important check before milestone 2.

```bash
python -m src.model \
  --data bq://valore-mlsd-project.valore.housing_raw \
  --project_id valore-mlsd-project \
  --target price \
  --out_dir models/baseline_recheck
```

This should create:

* `models/baseline_recheck/model.joblib`
* `models/baseline_recheck/metrics.json`
* `models/baseline_recheck/best_params.json`
* `models/baseline_recheck/val_baselines.csv`
