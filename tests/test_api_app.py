from unittest.mock import patch

from fastapi.testclient import TestClient

import src.api.app as app_module
from src.api.app import PAST_PREDICTIONS, REQUIRED_FEATURES, app


class DummyPredictionModel:
    """Fake model that mimics the real one without loading a heavy joblib."""

    def predict(self, features):
        # Ensures preprocessing didn't drop or rename columns
        assert list(features.columns) == REQUIRED_FEATURES
        # $100k per bedroom so we can verify data flowed through
        n_bedrooms = features["bedrooms"].iloc[0]
        return [float(n_bedrooms * 100000.0)]


def _valid_payload():
    return {
        "data": {
            "id": "house-123",
            "date": "20141013T000000",
            "bedrooms": 3,
            "bathrooms": 2.5,
            "sqft_living": 1000,
            "sqft_lot": 5000,
            "floors": 2.0,
            "waterfront": 0,
            "view": 0,
            "condition": 3,
            "grade": 7,
            "sqft_above": 800,
            "sqft_basement": 200,
            "yr_built": 1990,
            "yr_renovated": 0,
            "zipcode": "98001",
            "lat": 47.5,
            "long": -122.2,
            "sqft_living15": 1100,
            "sqft_lot15": 5100,
        }
    }


def test_predict_success():
    with patch(
        "src.api.app.load_model_from_registry",
        return_value=DummyPredictionModel(),
    ):
        with TestClient(app) as client:
            app_module.model = DummyPredictionModel()
            PAST_PREDICTIONS.clear()

            response = client.post("/predict", json=_valid_payload())

            expected_price = 300000.0  # 3 bedrooms * 100,000
            assert response.status_code == 200
            assert response.json()["prediction"] == expected_price
            assert PAST_PREDICTIONS["house-123"]["prediction"] == expected_price


def test_predict_error_no_model():
    with patch("src.api.app.load_model_from_registry", return_value=None):
        with TestClient(app) as client:
            app_module.model = None

            response = client.post("/predict", json=_valid_payload())

            assert response.status_code == 500
            assert "Model not loaded" in response.json()["detail"]


def test_health_endpoint():
    with patch(
        "src.api.app.load_model_from_registry",
        return_value=DummyPredictionModel(),
    ):
        with TestClient(app) as client:
            app_module.model = DummyPredictionModel()

            response = client.get("/health")

            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
            assert response.json()["model_loaded"] is True


def test_get_past_predictions():
    with patch(
        "src.api.app.load_model_from_registry",
        return_value=DummyPredictionModel(),
    ):
        with TestClient(app) as client:
            PAST_PREDICTIONS.clear()
            PAST_PREDICTIONS["test-id"] = {
                "id": "test-id",
                "prediction": 500.0,
                "currency": "USD",
            }

            response = client.get("/past_predictions")

            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]["id"] == "test-id"
