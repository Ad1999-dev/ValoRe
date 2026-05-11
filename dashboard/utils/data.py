"""Data-source helpers: BigQuery, GCS, champion model scoring."""

import io

import pandas as pd
import streamlit as st

from utils.config import PROJECT_ID

# Feature order the served XGBoost model was trained with.
# Mirrors src/api/app.py REQUIRED_FEATURES — keep in sync if it changes.
MODEL_FEATURES = [
    "bedrooms",
    "bathrooms",
    "sqm_living",
    "sqm_lot",
    "floors",
    "waterfront",
    "view",
    "condition",
    "grade",
    "yr_built",
    "yr_renovated",
    "lat",
    "long",
    "sqm_living15",
    "sqm_lot15",
    "basement_ratio",
    "year",
    "month",
    "day",
    "dayofweek",
]


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


def _clean_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """Reproduce src.modeling.preprocessing.clean_dataframe for the dashboard env.

    Kept local because the dashboard image does not vendor the training package.
    Any change here must mirror src/modeling/preprocessing.py.
    """
    df = df.copy()

    sqft_cols = [c for c in df.columns if "sqft" in c]
    if sqft_cols:
        df[sqft_cols] = df[sqft_cols] * 0.092903
        df = df.rename(columns={c: c.replace("sqft", "sqm") for c in sqft_cols})

    if "sqm_basement" in df.columns and "sqm_living" in df.columns:
        df["basement_ratio"] = df["sqm_basement"] / df["sqm_living"]
        df["basement_ratio"] = df["basement_ratio"].fillna(0.0)

    drop_now = [
        c for c in ("id", "zipcode", "sqm_basement", "sqm_above") if c in df.columns
    ]
    if drop_now:
        df = df.drop(columns=drop_now)

    if "date" in df.columns:
        dt = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = dt.dt.year
        df["month"] = dt.dt.month
        df["day"] = dt.dt.day
        df["dayofweek"] = dt.dt.dayofweek
        df = df.drop(columns=["date"])

    return df


@st.cache_resource(show_spinner=False)
def load_champion_model(artifact_uri: str):
    """Download the champion model.joblib from GCS and load it. Cached per URI."""
    import gcsfs
    import joblib

    fs = gcsfs.GCSFileSystem(project=PROJECT_ID)
    path = artifact_uri.rstrip("/") + "/model.joblib"
    with fs.open(path, "rb") as f:
        buf = io.BytesIO(f.read())
    return joblib.load(buf)


def get_feature_importances(model, feature_names: list[str]) -> pd.DataFrame | None:
    """Unwrap a Pipeline / GridSearchCV and return per-feature importances."""
    est = model
    if hasattr(est, "best_estimator_"):
        est = est.best_estimator_
    if hasattr(est, "named_steps"):
        for step in est.named_steps.values():
            if hasattr(step, "feature_importances_"):
                est = step
                break
    if not hasattr(est, "feature_importances_"):
        return None
    importances = list(est.feature_importances_)
    if len(importances) != len(feature_names):
        return None
    return pd.DataFrame({"feature": feature_names, "importance": importances})


@st.cache_data(ttl=600, show_spinner=False)
def score_sample(artifact_uri: str, n: int = 2000) -> pd.DataFrame:
    """Sample BigQuery, run through the champion model, return actual/predicted/residual."""
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)
    # Hash-based pseudo-random sample — stable per query, no full table scan needed.
    query = f"""
        SELECT price, lat, long, bedrooms, bathrooms,
               sqft_living, sqft_lot, floors, waterfront,
               view, condition, grade, yr_built, yr_renovated,
               sqft_above, sqft_basement,
               sqft_living15, sqft_lot15, date
        FROM `{PROJECT_ID}.valore.housing_raw`
        WHERE MOD(ABS(FARM_FINGERPRINT(CAST(date AS STRING) || CAST(lat AS STRING))), 100) < 15
        LIMIT {n}
    """
    raw = client.query(query).to_dataframe()
    if raw.empty:
        return pd.DataFrame(columns=["actual", "predicted", "residual"])

    actual = raw["price"].astype(float).reset_index(drop=True)
    feats = _clean_for_model(raw.drop(columns=["price"]))
    X = feats[MODEL_FEATURES]

    model = load_champion_model(artifact_uri)
    predicted = pd.Series(model.predict(X), name="predicted").astype(float)

    return pd.DataFrame(
        {
            "actual": actual,
            "predicted": predicted.reset_index(drop=True),
            "residual": (actual - predicted.reset_index(drop=True)),
        }
    )
