from google.api_core.exceptions import Conflict
from google.cloud import storage


def get_gcs_client(project_id):
    return storage.Client(project=project_id)


def create_bucket(project_id, bucket_name, location="europe-west1"):
    client = get_gcs_client(project_id)
    bucket = client.bucket(bucket_name)

    try:
        new_bucket = client.create_bucket(bucket, location=location)
        print(f"Bucket created: {new_bucket.name} ({new_bucket.location})")
    except Conflict:
        # A 409 Conflict can mean either that the bucket already exists and is
        # accessible to this project, or that the name is taken by another
        # project (or otherwise inaccessible). Check accessibility explicitly.
        existing_bucket = client.lookup_bucket(bucket_name)
        if existing_bucket is None:
            raise RuntimeError(
                f"Bucket name '{bucket_name}' is already in use or not accessible "
                f"for project '{project_id}'. Choose a different bucket name or "
                f"verify that you have access to the bucket."
            )
        print(f"Bucket already exists and is accessible: {existing_bucket.name} ({existing_bucket.location})")


def upload_file(project_id, bucket_name, local_path, blob_path):
    client = get_gcs_client(project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)
    print(f"Uploaded: {local_path} -> gs://{bucket_name}/{blob_path}")


def download_file(project_id, bucket_name, blob_path, local_path):
    client = get_gcs_client(project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)
    print(f"Downloaded: gs://{bucket_name}/{blob_path} -> {local_path}")


def list_files(project_id, bucket_name, prefix=None):
    client = get_gcs_client(project_id)
    blobs = client.list_blobs(bucket_name, prefix=prefix)

    print(f"Files in gs://{bucket_name}/{prefix or ''}")
    for blob in blobs:
        print(blob.name)
