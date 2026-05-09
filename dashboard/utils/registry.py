"""Vertex AI Model Registry helpers."""

import streamlit as st

from utils.config import MODEL_DISPLAY_NAME, PROJECT_ID, REGION


@st.cache_data(ttl=300, show_spinner=False)
def list_model_versions() -> list[dict]:
    """Return all registered ValoRe model versions, newest first.

    Each dict has: version_id, create_time, is_default, labels, artifact_uri.
    Returns [] on any error so callers can degrade gracefully.
    """
    try:
        from google.cloud import aiplatform

        aiplatform.init(project=PROJECT_ID, location=REGION)
        models = aiplatform.Model.list(
            filter=f'display_name="{MODEL_DISPLAY_NAME}"',
            order_by="create_time desc",
        )
    except Exception:
        return []

    out = []
    for m in models:
        out.append(
            {
                "version_id": m.version_id,
                "create_time": m.create_time,
                "is_default": "default" in (m.version_aliases or []),
                "labels": dict(m.labels or {}),
                "artifact_uri": m.uri,
            }
        )
    return out
