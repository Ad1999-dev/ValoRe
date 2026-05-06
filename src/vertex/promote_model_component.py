from kfp.dsl import Input, Metrics, Model, component

from src.config import VERTEX_BASE_IMAGE


@component(base_image=VERTEX_BASE_IMAGE)
def promote_model_component(
    model: Input[Model],
    metrics: Input[Metrics],
    project_id: str,
    region: str,
    gcs_bucket: str,
    model_display_name: str,
):
    """
    Copies the trained model artifact to a stable versioned GCS path and
    registers it in Vertex AI Model Registry as a new version.

    The API loads the model by querying the registry for the default version
    of `model_display_name` — no manual path updates needed after each run.
    """
    from datetime import datetime, timezone

    from google.cloud import aiplatform, storage

    # ── 1. Copy model to a stable, human-readable GCS path ──────────────────
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    dest_blob = f"models/registry/{run_ts}/model.joblib"
    dest_gcs_dir = f"gs://{gcs_bucket}/models/registry/{run_ts}/"

    gcs_client = storage.Client(project=project_id)
    bucket_obj = gcs_client.bucket(gcs_bucket)
    blob = bucket_obj.blob(dest_blob)
    blob.upload_from_filename(model.path)
    print(f"Model copied to {dest_gcs_dir}")

    # ── 2. Register in Vertex AI Model Registry ──────────────────────────────
    aiplatform.init(project=project_id, location=region)

    # Look up existing model to create a new version under it (preserves history).
    # On the very first run there is no existing model, so parent_model=None.
    existing = aiplatform.Model.list(
        filter=f'display_name="{model_display_name}"',
        order_by="create_time desc",
    )
    parent_model = existing[0].resource_name if existing else None

    # Retrieve logged metrics to attach as labels for easy identification.
    test_r2 = metrics.metadata.get("test_r2", 0.0)
    test_rmse = metrics.metadata.get("test_rmse", 0.0)

    vertex_model = aiplatform.Model.upload(
        display_name=model_display_name,
        artifact_uri=dest_gcs_dir,
        # Pre-built sklearn container satisfies the required field.
        # The API uses joblib directly — this container is not used for serving.
        serving_container_image_uri=(
            "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-5:latest"
        ),
        parent_model=parent_model,
        is_default_version=True,
        labels={
            # GCP labels: lowercase letters, numbers, underscores, hyphens only.
            "trained_at": run_ts.replace("T", "-"),
            "test_r2": str(round(float(test_r2), 4)).replace(".", "_"),
            "test_rmse": str(round(float(test_rmse), 2)).replace(".", "_"),
        },
    )

    print(f"Registered model : {vertex_model.resource_name}")
    print(f"Version          : {vertex_model.version_id}")
    print(f"Artifact URI     : {dest_gcs_dir}")
