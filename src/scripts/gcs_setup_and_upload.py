from src.cloud.gcs_io import create_bucket, list_files, upload_file
from src.config import (
    GCS_BUCKET_NAME,
    GCS_RAW_BLOB_PATH,
    LOCAL_CSV_PATH,
    PROJECT_ID,
    REGION,
)


def main():
    create_bucket(PROJECT_ID, GCS_BUCKET_NAME, location=REGION)
    upload_file(PROJECT_ID, GCS_BUCKET_NAME, str(LOCAL_CSV_PATH), GCS_RAW_BLOB_PATH)
    list_files(PROJECT_ID, GCS_BUCKET_NAME, prefix="data/")


if __name__ == "__main__":
    main()
