from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import boto3
import joblib
import json
import os
import tempfile

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


S3_BUCKET = os.getenv("S3_BUCKET", "async-ai-inference")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

MODEL_KEY = "final-project/model/model.pkl"
TEST_DATA_KEY = "final-project/data/test_data.json"


def train_and_upload_model():
    data = load_breast_cancer()
    X = data.data
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = LogisticRegression(max_iter=5000)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Model accuracy: {accuracy}")

    s3 = boto3.client("s3", region_name=AWS_REGION)

    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.pkl")
        test_data_path = os.path.join(tmpdir, "test_data.json")

        joblib.dump(model, model_path)

        test_records = []

        for i, features in enumerate(X_test):
            test_records.append({
                "record_id": f"sample_{i:03d}",
                "features": features.tolist(),
                "actual": int(y_test[i])
            })

        with open(test_data_path, "w") as f:
            json.dump(test_records, f)

        s3.upload_file(model_path, S3_BUCKET, MODEL_KEY)
        s3.upload_file(test_data_path, S3_BUCKET, TEST_DATA_KEY)

    print(f"Uploaded model to s3://{S3_BUCKET}/{MODEL_KEY}")
    print(f"Uploaded test data to s3://{S3_BUCKET}/{TEST_DATA_KEY}")


with DAG(
    dag_id="train_breast_cancer_model",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["final-project", "training"],
) as dag:

    train_task = PythonOperator(
        task_id="train_and_upload_model",
        python_callable=train_and_upload_model
    )