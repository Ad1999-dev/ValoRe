from kfp import compiler, dsl
from google.cloud import aiplatform

from src.config import (
    BQ_DATASET_ID,
    BQ_TABLE_NAME,
    PROJECT_ID,
    REGION,
    VERTEX_PIPELINE_JSON,
    VERTEX_PIPELINE_ROOT,
)
from src.vertex.data_ingestion import data_ingestion
from src.vertex.evaluation_component import evaluation_component
from src.vertex.preprocessing_component import preprocessing_component
from src.vertex.splitting_component import splitting_component
from src.vertex.training_component import training_component


@dsl.pipeline(
    name="valore-pipeline",
    pipeline_root=VERTEX_PIPELINE_ROOT,
)
def valore_pipeline(
    bq_project: str = PROJECT_ID,
    bq_dataset: str = BQ_DATASET_ID,
    bq_table: str = BQ_TABLE_NAME,
    target_col: str = "price",
    model_name: str = "xgboost",
):
    ingestion_task = data_ingestion(
        bq_project=bq_project,
        bq_dataset=bq_dataset,
        bq_table=bq_table,
    )

    preprocessing_task = preprocessing_component(
        input_dataset=ingestion_task.outputs["dataset"],
    )

    splitting_task = splitting_component(
        processed_dataset=preprocessing_task.outputs["processed_dataset"],
        test_size=0.2,
        seed=42,
    )

    training_task = training_component(
        train_dataset=splitting_task.outputs["train_dataset"],
        target_col=target_col,
        model_name=model_name,
        seed=42,
        cv_folds=5,
    )

    evaluation_component(
        model=training_task.outputs["model"],
        test_dataset=splitting_task.outputs["test_dataset"],
        target_col=target_col,
    )


def main():
    compiler.Compiler().compile(
        pipeline_func=valore_pipeline,
        package_path=str(VERTEX_PIPELINE_JSON),
    )

    aiplatform.init(
        project=PROJECT_ID,
        location=REGION,
    )

    job = aiplatform.PipelineJob(
        display_name="valore-pipeline-run",
        template_path=str(VERTEX_PIPELINE_JSON),
        pipeline_root=VERTEX_PIPELINE_ROOT,
        parameter_values={
            "bq_project": PROJECT_ID,
            "bq_dataset": BQ_DATASET_ID,
            "bq_table": BQ_TABLE_NAME,
            "target_col": "price",
            "model_name": "xgboost",
        },
    )

    job.run(sync=True)


if __name__ == "__main__":
    main()