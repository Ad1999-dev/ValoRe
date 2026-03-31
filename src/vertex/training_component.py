from kfp.dsl import Dataset, Input, Metrics, Model, Output, component

from src.config import VERTEX_BASE_IMAGE


@component(base_image=VERTEX_BASE_IMAGE)
def training_component(
    train_dataset: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics],
    target_col: str = "price",
    model_name: str = "xgboost",
    seed: int = 42,
    cv_folds: int = 5,
):
    import joblib
    import os

    import pandas as pd

    from src.modeling.model_selection import run_grid_search
    from src.modeling.training import fit_final_model

    train_path = os.path.join(train_dataset.path, "train.parquet")
    train_df = pd.read_parquet(train_path)

    result = run_grid_search(
        train_df=train_df,
        target_col=target_col,
        model_name=model_name,
        random_state=seed,
        cv_folds=cv_folds,
    )

    best_model = result["best_estimator"]
    best_params = result["best_params"]
    best_cv_rmse = result["best_cv_rmse"]

    best_model = fit_final_model(best_model, train_df, target_col)

    joblib.dump(best_model, model.path)

    if best_cv_rmse is not None:
        metrics.log_metric("best_cv_rmse", float(best_cv_rmse))

    print("Best params: {}".format(best_params))
    print("Saved trained model to {}".format(model.path))