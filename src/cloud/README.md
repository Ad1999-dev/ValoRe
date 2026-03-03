# Cloud utilities (`src/cloud/`)

This folder contains reusable helper functions for cloud operations.

## Files
- `bigquery_io.py`
  - Create datasets
  - Load pandas DataFrames into BigQuery tables
  - Run SQL queries and return pandas DataFrames

- `gcs_io.py`
  - Create buckets
  - Upload and download files
  - List objects in a bucket

## Why this exists
In MLOps, we avoid duplicating cloud logic across notebooks and scripts.
These utilities are imported by scripts and (later) by training pipelines.
