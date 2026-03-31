from kfp.dsl import Dataset, Input, Output, component

from src.config import VERTEX_BASE_IMAGE


@component(base_image=VERTEX_BASE_IMAGE)
def preprocessing_component(
    input_dataset: Input[Dataset],
    processed_dataset: Output[Dataset],
):
    import glob
    import os

    import pandas as pd

    from src.modeling.preprocessing import clean_dataframe

    parquet_files = glob.glob(os.path.join(input_dataset.path, "*.parquet"))

    if not parquet_files:
        raise ValueError("No parquet files found in {}".format(input_dataset.path))

    frames = []
    for file_path in parquet_files:
        frames.append(pd.read_parquet(file_path))

    df = pd.concat(frames, ignore_index=True)
    df = clean_dataframe(df)

    os.makedirs(processed_dataset.path, exist_ok=True)
    output_path = os.path.join(processed_dataset.path, "data.parquet")
    df.to_parquet(output_path, index=False)

    print("Saved processed data to {}".format(output_path))