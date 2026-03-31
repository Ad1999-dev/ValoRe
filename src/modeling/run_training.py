import argparse
from pathlib import Path

import joblib
import pandas as pd

from src.config import BEST_PARAMS_FILE, METRICS_FILE, MODEL_FILE, MODELS_DIR
from src.modeling.data_loading import load_dataframe
from src.modeling.evaluation import evaluate_regression, save_json
from src.modeling.model_selection import run_grid_search
from src.modeling.preprocessing import clean_dataframe
from src.modeling.splitting import split_train_test
from src.modeling.training import fit_final_model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to CSV or bq://project.dataset.table",
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=None,
        help="GCP project id (optional)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="price",
        help="Target column name",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="xgboost",
        choices=[
            "dummy",
            "linear_regression",
            "knn",
            "random_forest",
            "xgboost",
        ],
        help="Which model family to train",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=str(MODELS_DIR),
        help="Folder to save outputs",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--cv_folds", type=int, default=5)

    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    df = load_dataframe(args.data, project_id=args.project_id)

    print("Cleaning and preprocessing data...")
    df = clean_dataframe(df)

    print("Creating train and test split...")
    train_df, test_df = split_train_test(
        df,
        test_size=args.test_size,
        random_state=args.seed,
    )

    print("Running model selection for '{}'...".format(args.model_name))
    selection_result = run_grid_search(
        train_df=train_df,
        target_col=args.target,
        model_name=args.model_name,
        random_state=args.seed,
        cv_folds=args.cv_folds,
    )

    best_model = selection_result["best_estimator"]
    best_params = selection_result["best_params"]
    best_cv_rmse = selection_result["best_cv_rmse"]

    print("Best parameters:")
    print(best_params)

    if best_cv_rmse is not None:
        print("Best CV RMSE: {:.4f}".format(best_cv_rmse))

    print("Fitting final model on the training dataframe...")
    best_model = fit_final_model(best_model, train_df, args.target)

    print("Evaluating on the test dataframe...")
    test_metrics = evaluate_regression(best_model, test_df, args.target)

    print("Test metrics:")
    print(test_metrics)

    metrics_payload = {
        "data_source": args.data,
        "target": args.target,
        "model_name": args.model_name,
        "n_rows": int(len(df)),
        "n_train_rows": int(len(train_df)),
        "n_test_rows": int(len(test_df)),
        "best_params": best_params,
        "best_cv_rmse": best_cv_rmse,
        "test_metrics": test_metrics,
    }

    joblib.dump(best_model, out_dir / MODEL_FILE.name)
    save_json(metrics_payload, out_dir / METRICS_FILE.name)
    save_json(best_params, out_dir / BEST_PARAMS_FILE.name)

    summary_df = pd.DataFrame(
        [
            {
                "model": args.model_name,
                "test_mae": test_metrics["mae"],
                "test_rmse": test_metrics["rmse"],
                "test_r2": test_metrics["r2"],
            }
        ]
    )
    summary_df.to_csv(out_dir / "training_summary.csv", index=False)

    print("Saved model to: {}".format(out_dir / MODEL_FILE.name))
    print("Saved metrics to: {}".format(out_dir / METRICS_FILE.name))
    print("Saved params to: {}".format(out_dir / BEST_PARAMS_FILE.name))


if __name__ == "__main__":
    main()