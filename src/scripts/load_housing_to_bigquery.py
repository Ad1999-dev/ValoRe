import pandas as pd

from src.cloud.bigquery_io import create_dataset, load_dataframe_to_table
from src.cloud.gcs_io import download_file  # only needed for Option B


# -------------------------
# Fill in these settings
# -------------------------
PROJECT_ID = "valore-mlsd-project"
DATASET_ID = "valore"
TABLE_NAME = "housing_raw"
LOCATION = "europe-west1"

# Option A: local CSV path (NOT tracked in git)
# LOCAL_CSV_PATH = r"./data/raw/Housing.csv"  # Windows
LOCAL_CSV_PATH = "./data/raw/Housing.csv"  # Linux/Mac

# Option B: download from GCS then load into BigQuery
USE_GCS_DOWNLOAD = True
GCS_BUCKET = "mlsd-valore-2026-0001"
GCS_BLOB = "data/raw/Housing.csv"
TMP_CSV_PATH = "Housing_tmp.csv"


def main():
    # 1) Make sure dataset exists
    create_dataset(PROJECT_ID, DATASET_ID, location=LOCATION)

    # 2) Get CSV locally (either already local OR download from GCS)
    if USE_GCS_DOWNLOAD:
        download_file(PROJECT_ID, GCS_BUCKET, GCS_BLOB, TMP_CSV_PATH)
        csv_path = TMP_CSV_PATH
    else:
        csv_path = LOCAL_CSV_PATH

    # 3) Load into pandas
    df = pd.read_csv(csv_path)

    # 4) Upload DataFrame into BigQuery table
    load_dataframe_to_table(df, PROJECT_ID, DATASET_ID, TABLE_NAME)


if __name__ == "__main__":
    main()