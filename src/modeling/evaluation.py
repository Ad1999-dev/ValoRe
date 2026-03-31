import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def evaluate_regression(model, df, target_col):
    """
    Evaluate a fitted model on a dataframe that still contains the target.
    """
    if target_col not in df.columns:
        raise ValueError("Target column '{}' not found in dataframe".format(target_col))

    X = df.drop(columns=[target_col])
    y = df[target_col]
    pred = model.predict(X)

    return {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": rmse(y, pred),
        "r2": float(r2_score(y, pred)),
    }


def save_json(data, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def compute_permutation_importance(
    model,
    df,
    target_col,
    random_state=42,
    n_repeats=10,
):
    """
    Compute permutation importance on a dataframe.
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    result = permutation_importance(
        model,
        X,
        y,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=-1,
    )

    importance_df = pd.DataFrame(
        {
            "feature": X.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )

    importance_df = importance_df.sort_values(
        "importance_mean",
        ascending=False,
    ).reset_index(drop=True)

    return importance_df