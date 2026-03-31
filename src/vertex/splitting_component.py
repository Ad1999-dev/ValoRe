from kfp.dsl import Dataset, Input, Output, component

from src.config import VERTEX_BASE_IMAGE


@component(base_image=VERTEX_BASE_IMAGE)
def splitting_component(
    processed_dataset: Input[Dataset],
    train_dataset: Output[Dataset],
    test_dataset: Output[Dataset],
    test_size: float = 0.2,
    seed: int = 42,
):
    import os

    import pandas as pd

    from src.modeling.splitting import split_train_test

    input_path = os.path.join(processed_dataset.path, "data.parquet")
    df = pd.read_parquet(input_path)

    train_df, test_df = split_train_test(
        df,
        test_size=test_size,
        random_state=seed,
    )

    os.makedirs(train_dataset.path, exist_ok=True)
    os.makedirs(test_dataset.path, exist_ok=True)

    train_df.to_parquet(os.path.join(train_dataset.path, "train.parquet"), index=False)
    test_df.to_parquet(os.path.join(test_dataset.path, "test.parquet"), index=False)

    print("Saved split datasets.")