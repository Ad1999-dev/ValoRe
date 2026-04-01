import io
import os

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google.cloud import storage
from pydantic import BaseModel, Field

# Import our custom logic
from src.modeling.preprocessing import clean_dataframe

app = FastAPI(
    title="King County house price predictor",
    description="An API to predict housing prices using a model fetched from GCS.",
    version="1.1.0",
)

templates = Jinja2Templates(directory="templates")

# In-memory database for predictions
PAST_PREDICTIONS = {}

# The 20 features your model specifically expects
REQUIRED_FEATURES = [
    "bedrooms",
    "bathrooms",
    "sqm_living",
    "sqm_lot",
    "floors",
    "waterfront",
    "view",
    "condition",
    "grade",
    "yr_built",
    "yr_renovated",
    "lat",
    "long",
    "sqm_living15",
    "sqm_lot15",
    "basement_ratio",
    "year",
    "month",
    "day",
    "dayofweek",
]

# Global model variable
model = None


def load_model_from_gcs():
    """
    Fetches the model binary from Google Cloud Storage.
    Expects MODEL_PATH env var (e.g., gs://bucket-name/folder/model_file)
    """
    model_uri = os.getenv("MODEL_PATH")

    if not model_uri:
        print("CRITICAL: MODEL_PATH environment variable is not set.")
        return None

    try:
        print(f"Attempting to load model from: {model_uri}")
        client = storage.Client()
        # This helper automatically parses the gs:// string
        blob = storage.Blob.from_string(model_uri, client=client)

        # Download the binary data into a byte stream
        buffer = io.BytesIO()
        blob.download_to_file(buffer)
        buffer.seek(0)

        # Load the model directly from the stream
        loaded_model = joblib.load(buffer)
        print("Model loaded successfully from GCS!")
        return loaded_model
    except Exception as e:
        print(f"Error loading model from GCS: {e}")
        return None


@app.on_event("startup")
async def startup_event():
    """Runs when the container starts up."""
    global model
    model = load_model_from_gcs()


class HouseData(BaseModel):
    # Identifiers & Dates (No bounds needed, pattern handles date)
    id: str = Field(..., description="Property identifier")
    date: str = Field(..., pattern=r"^\d{8}T000000$", description="YYYYMMDDT000000")

    # Physical Attributes (Min bounds only)
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0.0)
    sqft_living: int = Field(..., ge=0)
    sqft_lot: int = Field(..., ge=0)
    floors: float = Field(..., ge=1.0)  # Logic: Must have at least 1 floor

    # Categorical / Ordinal (Min bounds only)
    # Note: Model might act weird if view/condition/grade exceed original scales
    waterfront: int = Field(..., ge=0)
    view: int = Field(..., ge=0)
    condition: int = Field(..., ge=1)
    grade: int = Field(..., ge=1)

    # Area breakdown (Min bounds only)
    sqft_above: int = Field(..., ge=0)
    sqft_basement: int = Field(..., ge=0)

    # Years (Logic: Built year can't be negative)
    yr_built: int = Field(..., ge=0)
    yr_renovated: int = Field(..., ge=0)

    # Location (Removed specific lat/long bounds, keeping patterns for zipcode)
    zipcode: str = Field(...)
    lat: float = Field(...)
    long: float = Field(...)

    # Neighborhood Context (Min bounds only)
    sqft_living15: int = Field(..., ge=0)
    sqft_lot15: int = Field(..., ge=0)


class PredictionPayload(BaseModel):
    # This wraps the HouseData inside a "data" key to match the requirements
    data: HouseData


class UpdatePayload(BaseModel):
    # Enforcing the target range from your data card
    prediction: float = Field(
        ...,
        example=10000,
        ge=1000,
        le=10000000,
        description="The corrected house price prediction in USD",
    )


@app.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "ValoRe (house price predictor) API"},
    )


@app.post("/predict")
async def predict(payload: PredictionPayload):
    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Check MODEL_PATH and IAM permissions.",
        )

    try:
        input_dict = payload.data.model_dump()
        record_id = str(input_dict.get("id", "unknown"))

        # Convert input to DataFrame
        df = pd.DataFrame([input_dict])

        # Apply your custom feature engineering
        df = clean_dataframe(df)

        # Check for missing columns before predicting
        missing_cols = set(REQUIRED_FEATURES) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns after preprocessing: {missing_cols}")

        # Ensure features are in the exact order the model was trained on
        X = df[REQUIRED_FEATURES]

        # Run prediction
        pred = model.predict(X)
        prediction_value = float(pred[0])

        # Store in history
        PAST_PREDICTIONS[record_id] = {
            "id": record_id,
            "prediction": prediction_value,
            "currency": "USD",
        }

        return {"prediction": prediction_value, "currency": "USD", "status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/past_predictions")
async def get_past_predictions():
    return list(PAST_PREDICTIONS.values())


@app.put("/past_predictions/{record_id}")
async def update_prediction(record_id: str, payload: UpdatePayload):
    if record_id not in PAST_PREDICTIONS:
        raise HTTPException(status_code=404, detail="Prediction ID not found.")

    PAST_PREDICTIONS[record_id]["prediction"] = payload.prediction
    return {"message": "Updated successfully", "data": PAST_PREDICTIONS[record_id]}


@app.get("/health")
async def health():
    return {
        "status": "healthy" if model else "unhealthy",
        "model_loaded": model is not None,
        "model_path": os.getenv("MODEL_PATH", "Not Set"),
    }
