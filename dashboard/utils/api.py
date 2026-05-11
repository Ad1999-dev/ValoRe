"""HTTP helpers for the ValoRe prediction API."""

import requests
import streamlit as st

from utils.config import API_URL


def predict(house_data: dict) -> dict:
    """POST /predict — returns {"prediction": float, "currency": "USD", "status": "success"}."""
    response = requests.post(
        f"{API_URL}/predict",
        json={"data": house_data},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def health() -> dict:
    """GET /health — cached 60 s. Raises on non-2xx so callers can detect API down."""
    response = requests.get(f"{API_URL}/health", timeout=10)
    response.raise_for_status()
    return response.json()
