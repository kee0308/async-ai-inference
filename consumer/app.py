import boto3
import json
import joblib
import os
import tempfile
import time
from datetime import datetime, timezone

import numpy as np


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "async-ai-inference")
SQS_QUEUE_URL = os.getenv(
    "SQS_QUEUE_URL",
    "https://sqs.us-east-1.amazonaws.com/314226641988/async-ai-inference-queue"
)

MODEL_KEY = "final-project/model/model.pkl"
PREDICTION_PREFIX = "final-project/predictions/"


s3 = boto3.client("s3", region_name=AWS_REGION)
sqs = boto3.client("sqs", region_name=AWS_REGION)


def load_model_from_s3():
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.pkl")
        s3.download_file(S3_BUCKET, MODEL_KEY, model_path)
        model = joblib.load(model_path)

    print("Model loaded from S3")
    return model


def write_prediction_to_s3(record_id, prediction):
    output = {
        "record_id": record_id,
        "prediction": int(prediction),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    output_key = f"{PREDICTION_PREFIX}{record_id}.json"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=output_key,
        Body=json.dumps(output),
        ContentType="application/json"
    )

    print(f"Wrote prediction: {output_key}")


def process_message(message, model):
    body = json.loads(message["Body"])

    record_id = body["record_id"]
    features = body["features"]

    X = np.array(features).reshape(1, -1)
    prediction = model.predict(X)[0]

    write_prediction_to_s3(record_id, prediction)

    sqs.delete_message(
        QueueUrl=SQS_QUEUE_URL,
        ReceiptHandle=message["ReceiptHandle"]
    )

    print(f"Deleted message for {record_id}")


def main():
    model = load_model_from_s3()
    print("Consumer started. Polling SQS...")

    while True:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=10,
            VisibilityTimeout=30
        )

        messages = response.get("Messages", [])

        if not messages:
            print("No messages found.")
            time.sleep(5)
            continue

        for message in messages:
            try:
                process_message(message, model)
            except Exception as e:
                print(f"Error processing message: {e}")
                print("Message not deleted, so it can be retried.")


if __name__ == "__main__":
    main()