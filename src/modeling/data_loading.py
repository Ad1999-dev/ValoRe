from pathlib import Path

import pandas as pd

from src.cloud.bigquery_io import query_to_dataframe


def load_dataframe(data_source: str, project_id: str | None = None) -> pd.DataFrame:
    """
    Load a dataframe either from BigQuery or from a local CSV file.

    Supported formats:
    - bq://project.dataset.table
    - local/path/to/file.csv
    """
    if data_source.startswith("bq://"):
        table_id = data_source.replace("bq://", "", 1).strip()
        sql = f"SELECT * FROM `{table_id}`"
        return query_to_dataframe(sql, project_id=project_id)

    return pd.read_csv(Path(data_source))