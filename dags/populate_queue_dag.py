from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import json
import os

S3_BUCKET = os.getenv("S3_BUCKET", "async-ai-inference")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SQS_QUEUE_URL = os.getenv(
    "SQS_QUEUE_URL",
    "https://sqs.us-east-1.amazonaws.com/314226641988/async-ai-inference-queue"
)

TEST_DATA_KEY = "final-project/data/test_data.json"

def send_test_records_to_sqs():
    s3 = boto3.client("s3", region_name=AWS_REGION)
    sqs = boto3.client("sqs", region_name=AWS_REGION)

    obj = s3.get_object(Bucket=S3_BUCKET, Key=TEST_DATA_KEY)
    records = json.loads(obj["Body"].read().decode("utf-8"))

    for record in records:
        message = {
            "record_id": record["record_id"],
            "features": record["features"]
        }

        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        print(f"Sent {record['record_id']}")

    print(f"Sent {len(records)} messages to SQS")

with DAG(
    dag_id="populate_sqs_inference_jobs",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["final-project", "sqs"],
) as dag:

    send_messages_task = PythonOperator(
        task_id="send_test_records_to_sqs",
        python_callable=send_test_records_to_sqs
    )