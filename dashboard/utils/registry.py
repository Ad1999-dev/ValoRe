"""Vertex AI Model Registry helpers."""

import streamlit as st

from utils.config import MODEL_DISPLAY_NAME, PROJECT_ID, REGION


@st.cache_data(ttl=300, show_spinner=False)
def list_model_versions() -> list[dict]:
    """Return all registered ValoRe model versions.

    Each dict has: version_id, create_time, is_default, labels, artifact_uri.
    Returns [] on any error so callers can degrade gracefully.

    Note: aiplatform.Model.list() returns *parent* models (one per display name),
    not versions. We iterate each parent's versioning_registry to pull every
    registered version, then fetch each as a versioned Model to retrieve its
    own labels and artifact_uri.
    """
    try:
        from google.cloud import aiplatform

        aiplatform.init(project=PROJECT_ID, location=REGION)
        parents = aiplatform.Model.list(
            filter=f'display_name="{MODEL_DISPLAY_NAME}"',
        )
    except Exception:
        return []

    out: list[dict] = []
    for parent in parents:
        try:
            version_infos = parent.versioning_registry.list_versions()
        except Exception:
            continue

        for vi in version_infos:
            try:
                versioned = aiplatform.Model(
                    model_name=parent.resource_name,
                    version=vi.version_id,
                )
                labels = dict(versioned.labels or {})
                artifact_uri = versioned.uri
            except Exception:
                labels = {}
                artifact_uri = ""

            out.append(
                {
                    "version_id": vi.version_id,
                    "create_time": vi.version_create_time,
                    "is_default": "default" in (vi.version_aliases or []),
                    "labels": labels,
                    "artifact_uri": artifact_uri,
                }
            )
    return out
