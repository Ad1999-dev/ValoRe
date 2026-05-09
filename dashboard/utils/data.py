"""Data-source helpers: BigQuery, GCS."""

import pandas as pd
import streamlit as st

from utils.config import PROJECT_ID


@st.cache_data(ttl=3600, show_spinner=False)
def load_housing() -> pd.DataFrame:
    """Load the full King County housing dataset from BigQuery. Cached 1 h."""
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT price, lat, long, bedrooms, bathrooms,
               sqft_living, sqft_lot, floors, waterfront,
               view, condition, grade, yr_built, yr_renovated,
               zipcode, sqft_above, sqft_basement,
               sqft_living15, sqft_lot15, date
        FROM `{PROJECT_ID}.valore.housing_raw`
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=600, show_spinner=False)
def load_test_predictions(artifact_uri: str) -> pd.DataFrame:
    """Read per-version test-prediction Parquet written by the evaluation component."""
    try:
        import gcsfs

        fs = gcsfs.GCSFileSystem(project=PROJECT_ID)
        path = artifact_uri.rstrip("/") + "/test_predictions.parquet"
        with fs.open(path, "rb") as f:
            return pd.read_parquet(f)
    except Exception:
        return pd.DataFrame(columns=["actual", "predicted"])


@st.cache_data(ttl=3600, show_spinner=False)
def load_training_slice(train_size: int) -> pd.DataFrame:
    """Return the first `train_size` rows by sale date from BigQuery."""
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT price, sqft_living, grade, yr_built, lat, long, date
        FROM `{PROJECT_ID}.valore.housing_raw`
        ORDER BY date ASC
        LIMIT {train_size}
    """
    return client.query(query).to_dataframe()
