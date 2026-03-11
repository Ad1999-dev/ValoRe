# Cloud Initialization

This document explains how to reproduce the cloud setup and load/query data online.

## Prerequisites
- Google Cloud SDK (gcloud) installed
- Python environment activated (`.venv`)
- Required packages installed:
  - `google-cloud-bigquery`
  - `db-dtypes`
  - `pandas`
  - `google-cloud-storage` (if using GCS scripts)

## Authenticate to Google Cloud
```bash
gcloud init
gcloud config set project PROJECT_ID
gcloud auth application-default login
```

If you get a quota mismatch:

```bash
gcloud auth application-default set-quota-project PROJECT_ID
```

## Enable BigQuery API

```bash
gcloud services enable bigquery.googleapis.com
```

(Optional) Enable Cloud Storage API

```bash
gcloud services enable storage.googleapis.com
```

## Create bucket + upload raw dataset to GCS

Edit `src/scripts/gcs_setup_and_upload.py` with:

* `PROJECT_ID`
* `BUCKET_NAME`
* `LOCAL_CSV_PATH`

Then run:

```bash
python -m src.scripts.gcs_setup_and_upload
```

## Load dataset into BigQuery

Edit `src/scripts/load_housing_to_bigquery.py` with:

* `PROJECT_ID`
* `LOCAL_CSV_PATH` OR set `USE_GCS_DOWNLOAD=True` and fill bucket/blob

Run:

```bash
python -m src.scripts.load_housing_to_bigquery
```

## Verify with SQL queries

Edit `src/scripts/check_bigquery_queries.py`:

* ensure correct target column name (e.g., `price`)

Run:

```bash
python -m src.scripts.check_bigquery_queries
```

Expected output:

* row count
* sample rows
* basic target statistics
