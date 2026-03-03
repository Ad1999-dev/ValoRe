import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, make_scorer

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor


SQFT_TO_SQM = 0.092903


def load_dataframe(data_arg: str, project_id: str | None = None) -> pd.DataFrame:
    """
    Load data from:
      - BigQuery table: bq://project.dataset.table  (SELECT * FROM table)
    """
    if data_arg.startswith("bq://"):
        table_id = data_arg.replace("bq://", "", 1).strip()
        sql = f"SELECT * FROM `{table_id}`"
        from src.cloud.bigquery_io import query_to_dataframe
        return query_to_dataframe(sql, project_id=project_id)

    return pd.read_csv(data_arg)


def pre_process(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-process the raw dataframe with steps from EDA.
    """
    df = df.copy()

    # Drop id
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # Parse date 
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    # Convert sqft columns to sqm and rename
    sqft_cols = [c for c in df.columns if "sqft" in c]
    if sqft_cols:
        df[sqft_cols] = df[sqft_cols] * SQFT_TO_SQM
        df = df.rename(columns={c: c.replace("sqft", "sqm") for c in sqft_cols})

    # Drop zipcode
    if "zipcode" in df.columns:
        df = df.drop(columns=["zipcode"])

    # Basement_ratio = sqm_basement / sqm_living
    if "sqm_basement" in df.columns and "sqm_living" in df.columns:
        df["basement_ratio"] = df["sqm_basement"] / df["sqm_living"]

    # Drop sqm_basement and sqm_above 
    drop_cols = [c for c in ["sqm_basement", "sqm_above"] if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    return df


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
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


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def evaluate_regression(model, X_eval, y_eval) -> Dict[str, float]:
    pred = model.predict(X_eval)
    return {
        "mae": float(mean_absolute_error(y_eval, pred)),
        "rmse": rmse(y_eval, pred),
        "r2": float(r2_score(y_eval, pred)),
    }


def build_preprocess(X: pd.DataFrame) -> Tuple[ColumnTransformer, list]:
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    preprocess = ColumnTransformer(
        transformers=[("num", numeric_transformer, num_cols)],
        remainder="drop",
    )
    return preprocess, num_cols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to CSV or bq://project.dataset.table")
    parser.add_argument("--project_id", type=str, default=None, help="GCP project id (optional)")
    parser.add_argument("--target", type=str, default="price", help="Target column name")
    parser.add_argument("--out_dir", type=str, default="models", help="Folder to save artifacts")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--val_size_total", type=float, default=0.1, help="Validation fraction of total data")
    parser.add_argument("--cv_folds", type=int, default=10)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load raw (BigQuery) -> pre-process -> add date features
    df = load_dataframe(args.data, project_id=args.project_id)
    df = pre_process(df)
    df = add_date_features(df)

    if args.target not in df.columns:
        raise ValueError(f"Target '{args.target}' not found. Columns: {list(df.columns)}")

    X = df.drop(columns=[args.target])
    y = df[args.target]

    preprocess, num_cols = build_preprocess(X)
    X = X[num_cols]

    # Split: test first
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    # Split train vs val from trainval so that val is val_size_total of total
    val_fraction_of_trainval = args.val_size_total / (1.0 - args.test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=val_fraction_of_trainval, random_state=args.seed
    )

    # Baselines (fit on train, evaluate on val)
    baselines = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(
            n_estimators=500, random_state=args.seed, n_jobs=-1
        ),
        "XGBoost": XGBRegressor(
            objective="reg:squarederror",
            n_estimators=500,
            learning_rate=0.2,
            max_depth=6,
            random_state=args.seed,
            n_jobs=-1,
        ),
    }

    baseline_rows = []
    for name, model in baselines.items():
        pipe = Pipeline([("preprocess", preprocess), ("model", model)])
        pipe.fit(X_train, y_train)
        m = evaluate_regression(pipe, X_val, y_val)
        baseline_rows.append({"model": name, **{f"val_{k}": v for k, v in m.items()}})

    baseline_df = pd.DataFrame(baseline_rows).sort_values("val_rmse", ascending=True)
    baseline_df.to_csv(out_dir / "val_baselines.csv", index=False)

    print("\nBaseline validation results:")
    print(baseline_df.to_string(index=False))

    # XGBoost tunning
    rmse_scorer = make_scorer(rmse, greater_is_better=False)
    cv_inner = KFold(n_splits=args.cv_folds, shuffle=True, random_state=args.seed)

    xgb_pipe = Pipeline(
        [
            ("preprocess", preprocess),
            (
                "model",
                XGBRegressor(
                    objective="reg:squarederror",
                    random_state=args.seed,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    param_grid = {
        "model__n_estimators": [300, 500, 800],
        "model__learning_rate": [0.05, 0.1, 0.2],
        "model__max_depth": [4, 6, 8],
    }

    search = GridSearchCV(
        estimator=xgb_pipe,
        param_grid=param_grid,
        scoring=rmse_scorer,
        cv=cv_inner,
        n_jobs=-1,
        verbose=1,
        return_train_score=False,
    )
    search.fit(X_train, y_train)

    best_xgb = search.best_estimator_
    best_params = search.best_params_
    best_cv_rmse = float(-search.best_score_)

    best_params_clean = {
        k: (float(v) if isinstance(v, (np.floating,)) else v)
        for k, v in best_params.items()
    }

    print("\nBest hyperparameters (CV on train):")
    print(json.dumps(best_params_clean, indent=2))
    print("Best CV RMSE:", best_cv_rmse)

    # External validation check
    tuned_val_metrics = evaluate_regression(best_xgb, X_val, y_val)
    print("\nTuned model validation metrics:")
    print(json.dumps(tuned_val_metrics, indent=2))

    # Final training on train+val, then test
    best_xgb.fit(X_trainval, y_trainval)
    test_metrics = evaluate_regression(best_xgb, X_test, y_test)
    print("\nFinal test metrics:")
    print(json.dumps(test_metrics, indent=2))

    # Save final model + metrics + params
    joblib.dump(best_xgb, out_dir / "model.joblib")

    artifacts: Dict[str, Any] = {
        "data_path": args.data,
        "project_id": args.project_id,
        "target": args.target,
        "seed": args.seed,
        "splits": {
            "test_size": args.test_size,
            "val_size_total": args.val_size_total,
        },
        "n_rows": int(df.shape[0]),
        "n_features": int(X.shape[1]),
        "baseline_val_table": "val_baselines.csv",
        "best_params": best_params_clean,
        "best_cv_rmse": best_cv_rmse,
        "tuned_val_metrics": tuned_val_metrics,
        "test_metrics": test_metrics,
    }

    (out_dir / "metrics.json").write_text(json.dumps(artifacts, indent=2), encoding="utf-8")
    (out_dir / "best_params.json").write_text(json.dumps(best_params_clean, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()