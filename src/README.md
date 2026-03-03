# Source code (`src/`)

This folder contains all Python code for the ValoRe project.

## Structure
- `cloud/`
  Reusable helpers for Google Cloud services:
  - `bigquery_io.py`: create dataset, load data, query to pandas DataFrame
  - `gcs_io.py`: create bucket, upload/download files (optional but useful)

- `scripts/`
  Small runnable scripts (one job each), mainly for Milestone 1:
  - `gcs_setup_and_upload.py`: create bucket + upload raw CSV to GCS
  - `load_housing_to_bigquery.py`: load Housing.csv into BigQuery table
  - `check_bigquery_queries.py`: verify BigQuery table with simple SQL queries

## How to run scripts
Run from the repository root using module execution:

```bash
python -m src.scripts.gcs_setup_and_upload
python -m src.scripts.load_housing_to_bigquery
python -m src.scripts.check_bigquery_queries
```
