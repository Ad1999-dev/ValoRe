"""Single source of truth for environment-driven configuration."""

import os

API_URL = os.getenv("API_URL", "https://valore-api-826612837630.europe-west1.run.app/")
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "valore-mlsd-project")
REGION = os.getenv("GCP_REGION", "europe-west1")
MODEL_DISPLAY_NAME = os.getenv("MODEL_DISPLAY_NAME", "valore-xgboost")
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME", "mlsd-valore-2026-0001")
