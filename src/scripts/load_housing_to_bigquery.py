import pandas as pd

from src.cloud.bigquery_io import create_dataset, load_dataframe_to_table
from src.cloud.gcs_io import download_file
from src.config import (
    BQ_DATASET_ID,
    BQ_TABLE_NAME,
    GCS_BUCKET_NAME,
    GCS_RAW_BLOB_PATH,
    LOCAL_CSV_PATH,
    PROJECT_ID,
    REGION,
    TMP_CSV_PATH,
)

USE_GCS_DOWNLOAD = True


def main():
    create_dataset(PROJECT_ID, BQ_DATASET_ID, location=REGION)

    if USE_GCS_DOWNLOAD:
        download_file(
            PROJECT_ID,
            GCS_BUCKET_NAME,
            GCS_RAW_BLOB_PATH,
            str(TMP_CSV_PATH),
        )
        csv_path = TMP_CSV_PATH
    else:
        csv_path = LOCAL_CSV_PATH

    df = pd.read_csv(csv_path)
    load_dataframe_to_table(df, PROJECT_ID, BQ_DATASET_ID, BQ_TABLE_NAME)


if __name__ == "__main__":
    main()
