# Scripts (`src/scripts/`)

This folder contains small runnable scripts used for Milestone 1.

## Scripts
- `gcs_setup_and_upload.py`
  Creates a GCS bucket (first time) and uploads the raw dataset file.

- `load_housing_to_bigquery.py`
  Loads Housing.csv into BigQuery (`valore.housing_raw`).

- `check_bigquery_queries.py`
  Runs basic SQL queries to verify the BigQuery table (row count, sample rows, basic stats).

## How to run
Run scripts from the repository root using:

```bash
python -m src.scripts.<script_name_without_py>
```

Example:

```bash
python -m src.scripts.load_housing_to_bigquery
```

## Notes

* Do not commit the dataset to Git.
* Scripts require Google Cloud authentication via `gcloud auth application-default login`.
  See `docs/run_instructions.md`.
