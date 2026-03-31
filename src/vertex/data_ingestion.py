from kfp.dsl import Dataset, Output, component

from src.config import VERTEX_BASE_IMAGE


@component(base_image=VERTEX_BASE_IMAGE)
def data_ingestion(
    bq_project: str,
    bq_dataset: str,
    bq_table: str,
    dataset: Output[Dataset],
):
    from google.cloud import bigquery

    client = bigquery.Client(project=bq_project)

    extract_job = client.extract_table(
        "{}.{}.{}".format(bq_project, bq_dataset, bq_table),
        destination_uris=["{}/*.parquet".format(dataset.uri)],
        job_config=bigquery.ExtractJobConfig(
            destination_format=bigquery.DestinationFormat.PARQUET
        ),
    )

    extract_job.result()
    print("Exported raw table to {}".format(dataset.uri))