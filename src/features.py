import pandas as pd

SQFT_TO_SQM = 0.092903


def pre_process(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the main preprocessing steps we decided on during EDA.
    This function is shared between training and inference.
    """
    df = df.copy()

    if "id" in df.columns:
        df = df.drop(columns=["id"])

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    sqft_cols = [col for col in df.columns if "sqft" in col]
    if sqft_cols:
        df[sqft_cols] = df[sqft_cols] * SQFT_TO_SQM
        df = df.rename(columns={col: col.replace("sqft", "sqm") for col in sqft_cols})

    if "zipcode" in df.columns:
        df = df.drop(columns=["zipcode"])

    if "sqm_basement" in df.columns and "sqm_living" in df.columns:
        df["basement_ratio"] = df["sqm_basement"] / df["sqm_living"]

    drop_cols = [col for col in ["sqm_basement", "sqm_above"] if col in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    return df


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand the date column into simple numeric features.
    """
    if "date" not in df.columns:
        return df

    dt = pd.to_datetime(df["date"], errors="coerce")

    df = df.copy()
    df["year"] = dt.dt.year
    df["month"] = dt.dt.month
    df["day"] = dt.dt.day
    df["dayofweek"] = dt.dt.dayofweek
    df = df.drop(columns=["date"])

    return df
