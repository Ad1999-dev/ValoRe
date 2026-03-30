from pathlib import Path

import joblib
import pandas as pd

from src.features import add_date_features, pre_process

DEFAULT_MODEL_PATH = Path("models/model.joblib")


def load_model(model_path: str | Path = DEFAULT_MODEL_PATH):
    """
    Load the saved trained model.
    """
    return joblib.load(model_path)


def predict_one(payload: dict, model_path: str | Path = DEFAULT_MODEL_PATH) -> float:
    """
    Take one JSON-like input payload, convert it to a one-row DataFrame,
    apply the same preprocessing as training, and return one prediction.
    """
    model = load_model(model_path)

    df = pd.DataFrame([payload])
    df = pre_process(df)
    df = add_date_features(df)

    pred = model.predict(df)
    return float(pred[0])
