# Architecture

## Goal
Support online EDA and baseline training using cloud-hosted data, with clean engineering practices.

## Components
### Data layer
- **BigQuery**: primary online dataset table  
  - `PROJECT_ID.valore.housing_raw`
- **GCS** (optional but recommended): raw dataset file + future artifacts  
  - `gs://BUCKET_NAME/data/raw/Housing.csv`

### Code layer
- `src/cloud/bigquery_io.py`: reusable BigQuery utilities (create dataset, query to DataFrame)
- `src/cloud/gcs_io.py`: reusable GCS utilities (upload/download)
- `src/scripts/load_housing_to_bigquery.py`: one-time ingestion script
- `src/scripts/check_bigquery_queries.py`: online EDA proof script

### CI/CD layer
- Ruff + pre-commit + pytest locally
- GitHub Actions runs checks on PRs to `develop` and `main`

## Data flow
1. (Optional) Upload raw CSV to GCS
2. Load CSV into BigQuery table (`housing_raw`)
3. Run SQL queries from BigQuery for EDA and training extraction
4. Baseline training uses BigQuery query $\to$ pandas DataFrame (in the next feature)
