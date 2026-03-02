# How to run

## 1) One-time cloud setup
- `gcloud init`
- `gcloud config set project valore-mlsd-project`
- `gcloud auth application-default login`
- enable BigQuery:
  - `gcloud services enable bigquery.googleapis.com`

## 2) Upload raw dataset to GCS (optional but recommended)
Run:
- `python src/scripts/gcs_setup_and_upload.py`

This creates the bucket (first time) and uploads:
- `Housing.csv` → `gs://YOUR_BUCKET_NAME/data/raw/Housing.csv`

## 3) Load dataset into BigQuery ( for online EDA + training)
Run:
- `python src/scripts/load_housing_to_bigquery.py`

This creates dataset `valore` (if needed) and loads table `housing_raw`.
