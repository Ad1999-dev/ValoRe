from kfp.dsl import Dataset, Input, Metrics, Model, Output, component

from src.config import VERTEX_BASE_IMAGE


@component(base_image=VERTEX_BASE_IMAGE)
def evaluation_component(
    model: Input[Model],
    test_dataset: Input[Dataset],
    metrics: Output[Metrics],
    target_col: str = "price",
):
    import os

    import joblib
    import pandas as pd

    from src.modeling.evaluation import evaluate_regression

    loaded_model = joblib.load(model.path)

    test_path = os.path.join(test_dataset.path, "test.parquet")
    test_df = pd.read_parquet(test_path)

    test_metrics = evaluate_regression(loaded_model, test_df, target_col)

    metrics.log_metric("test_mae", float(test_metrics["mae"]))
    metrics.log_metric("test_rmse", float(test_metrics["rmse"]))
    metrics.log_metric("test_r2", float(test_metrics["r2"]))

    print(f"Test metrics: {test_metrics}")
