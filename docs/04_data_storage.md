# Data storage decision

## Requirement from teaching staff
For Milestone 1, data must be **online** for EDA and training.  
Storing the dataset in Git or relying on local-only reads is not acceptable.

## Decision
We use:
1. **BigQuery** as the primary online data source for EDA and model training (SQL / OLAP).
2. **Google Cloud Storage (GCS)** as raw object storage (raw CSV and later artifacts).

## BigQuery location
- Dataset: `valore`
- Table: `housing_raw`
- Full table ID:
  - `valore-mlsd-project.valore.housing_raw`

## GCS location (raw file)
- Bucket: `gs://mlsd-valore-2026-0001/`
- Raw data object:
  - `gs://mlsd-valore-2026-0001/data/raw/Housing.csv`

## Why this setup is good
- BigQuery enables online EDA via SQL and supports repeatable training data extraction.
- GCS is ideal for raw files and later for model artifacts (models, metrics, logs).