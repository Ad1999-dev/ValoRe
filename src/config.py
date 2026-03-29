from pathlib import Path
import os

# Main GCP settings
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "valore-mlsd-project")
REGION = os.getenv("GCP_REGION", "europe-west1")

# BigQuery
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "valore")
BQ_TABLE_NAME = os.getenv("BQ_TABLE_NAME", "housing_raw")
BQ_TABLE_FULL = f"{PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_NAME}"

# Cloud Storage
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "mlsd-valore-2026-0001")
GCS_RAW_BLOB_PATH = os.getenv("GCS_RAW_BLOB_PATH", "data/raw/Housing.csv")

# Local paths
REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_DATA_DIR = REPO_ROOT / "data" / "raw"
LOCAL_CSV_PATH = LOCAL_DATA_DIR / "Housing.csv"
TMP_CSV_PATH = REPO_ROOT / "Housing_tmp.csv"

# Model / artifact paths
MODELS_DIR = REPO_ROOT / "models"
MODEL_FILE = MODELS_DIR / "model.joblib"
METRICS_FILE = MODELS_DIR / "metrics.json"
BEST_PARAMS_FILE = MODELS_DIR / "best_params.json"
BASELINES_FILE = MODELS_DIR / "val_baselines.csv"