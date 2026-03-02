from src.cloud.gcs_io import create_bucket, upload_file, list_files

# -------------------------
# Fill in these settings
# -------------------------
PROJECT_ID = "valore-mlsd-project"

# Bucket name must be globally unique
BUCKET_NAME = "mlsd-valore-2026-0001"
LOCATION = "europe-west1"

# Local dataset path (NOT tracked in git)
# LOCAL_CSV_PATH = r"./data/raw/Housing.csv"  # Windows
LOCAL_CSV_PATH = "./data/raw/Housing.csv"  # Linux/Mac

# Destination path inside the bucket
BLOB_PATH = "data/raw/Housing.csv"


def main():
    # Step 1: Create bucket (run once)
    # If bucket already exists, comment this line out.
    create_bucket(PROJECT_ID, BUCKET_NAME, location=LOCATION)

    # Step 2: Upload dataset
    upload_file(PROJECT_ID, BUCKET_NAME, LOCAL_CSV_PATH, BLOB_PATH)

    # Step 3: List files to verify
    list_files(PROJECT_ID, BUCKET_NAME, prefix="data/")


if __name__ == "__main__":
    main()