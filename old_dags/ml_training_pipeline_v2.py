from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowFailException
from datetime import datetime
import json
import os
import sys
import boto3

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from ml_pipeline.model import train_model

S3_BUCKET = "mlops-spring2026"
THRESHOLD = 0.94


def run_training(**context):
    metadata = train_model()
    context["ti"].xcom_push(key="model_version", value=metadata["model_version"])


def evaluate_model():
    with open("models/metrics.json", "r") as f:
        metrics = json.load(f)

    accuracy = metrics["accuracy"]
    print(f"Accuracy: {accuracy}")

    if accuracy < THRESHOLD:
        raise AirflowFailException(
            f"Model failed quality gate: accuracy {accuracy} < {THRESHOLD}"
        )

    print("Model passed evaluation")


def promote_model(**context):
    model_version = context["ti"].xcom_pull(task_ids="train_model", key="model_version")

    s3 = boto3.client("s3")
    prefix = f"models/{model_version}/"

    s3.upload_file("models/model.pkl", S3_BUCKET, prefix + "model.pkl")
    s3.upload_file("models/metrics.json", S3_BUCKET, prefix + "metrics.json")
    s3.upload_file("models/metadata.json", S3_BUCKET, prefix + "metadata.json")

    print(f"Uploaded artifacts to s3://{S3_BUCKET}/{prefix}")


with DAG(
    dag_id="ml_training_pipeline_v2",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=run_training,
    )

    evaluate_task = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model,
    )

    promote_task = PythonOperator(
        task_id="promote_model",
        python_callable=promote_model,
    )

    train_task >> evaluate_task >> promote_task