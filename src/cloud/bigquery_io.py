from google.cloud import bigquery


def get_bq_client(project_id=None):
    # project_id can be None if gcloud default project is set
    if project_id:
        return bigquery.Client(project=project_id)
    return bigquery.Client()


def create_dataset(project_id, dataset_id, location="europe-west1"):
    client = get_bq_client(project_id)
    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = location
    client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset ready: {project_id}.{dataset_id} ({location})")


def load_dataframe_to_table(df, project_id, dataset_id, table_name):
    client = get_bq_client(project_id)
    table_id = f"{project_id}.{dataset_id}.{table_name}"

    job = client.load_table_from_dataframe(df, table_id)
    job.result()  # wait for job to finish
    print(f"Loaded {len(df)} rows -> {table_id}")


def query_to_dataframe(sql, project_id=None):
    client = get_bq_client(project_id)
    job = client.query(sql)
    return job.to_dataframe()


def run_query(sql, project_id=None):
    # Use this if you don’t need pandas output
    client = get_bq_client(project_id)
    job = client.query(sql)
    return job.result()