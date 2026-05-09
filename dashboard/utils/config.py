"""Single source of truth for environment-driven configuration."""

import os

API_URL = os.getenv("API_URL", "http://localhost:8080")
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "valore-mlsd-project")
REGION = os.getenv("GCP_REGION", "europe-west1")
MODEL_DISPLAY_NAME = os.getenv("MODEL_DISPLAY_NAME", "valore-xgboost")
GCS_BUCKET = os.getenv("GCS_BUCKET_NAME", "mlsd-valore-2026-0001")
