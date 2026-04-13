import pandas as pd

SQFT_TO_SQM = 0.092903


def clean_dataframe(df):
    df = df.copy()

    if "id" in df.columns:
        df = df.drop(columns=["id"])

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    sqft_cols = [col for col in df.columns if "sqft" in col]
    if sqft_cols:
        df[sqft_cols] = df[sqft_cols] * SQFT_TO_SQM
        rename_map = {}
        for col in sqft_cols:
            rename_map[col] = col.replace("sqft", "sqm")
        df = df.rename(columns=rename_map)

    if "zipcode" in df.columns:
        df = df.drop(columns=["zipcode"])

    if "sqm_basement" in df.columns and "sqm_living" in df.columns:
        df["basement_ratio"] = df["sqm_basement"] / df["sqm_living"]

    drop_cols = []
    for col in ["sqm_basement", "sqm_above"]:
        if col in df.columns:
            drop_cols.append(col)

    if drop_cols:
        df = df.drop(columns=drop_cols)

    if "date" in df.columns:
        dt = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = dt.dt.year
        df["month"] = dt.dt.month
        df["day"] = dt.dt.day
        df["dayofweek"] = dt.dt.dayofweek
        df = df.drop(columns=["date"])

    return df
