# Async AI Inference System

## Overview

This project implements an asynchronous machine learning inference system using:

- **Apache Airflow** (orchestration)
- **Amazon S3** (storage)
- **Amazon SQS** (queue)
- **Docker** (containerized compute)
- **Kubernetes** (deployment & scaling)

The system trains a model, generates inference jobs, processes them asynchronously, and stores predictions in S3.

---

## System Architecture

```text
Airflow Training DAG
        ↓
S3: model.pkl and test_data.json
        ↓
Airflow Queue DAG
        ↓
SQS inference messages
        ↓
Docker Consumer
        ↓
S3 prediction JSON files
```

---

## Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/kee0308/async-ai-inference
cd async-ai-inference
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__LOAD_EXAMPLES=False

export AWS_REGION=us-east-1
export S3_BUCKET=async-ai-inference
export SQS_QUEUE_NAME=async-ai-inference-queue
export SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/314226641988/async-ai-inference-queue"
```

### 4. Initialize Airflow

```bash
airflow db init
```

Create an Airflow user:

```bash
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

### 5. Copy DAG Files

```bash
mkdir -p ~/airflow/dags
cp dags/train_model_dag.py ~/airflow/dags/
cp dags/populate_queue_dag.py ~/airflow/dags/
```

### 6. Start Airflow

**Terminal 1:**
```bash
airflow scheduler
```

**Terminal 2 (UI, optional):**
```bash
airflow webserver --port 8080
```

---

## Running the Pipeline

### 1. Train the Model

```bash
airflow dags trigger train_breast_cancer_model
```

This DAG:

- Loads the breast cancer dataset
- Splits into train/test sets
- Trains a Logistic Regression model
- Saves `model.pkl` to S3
- Saves `test_data.json` to S3

Verify outputs:

```bash
aws s3 ls s3://async-ai-inference/final-project/model/
aws s3 ls s3://async-ai-inference/final-project/data/
```

### 2. Send Inference Jobs to SQS

```bash
airflow dags trigger populate_sqs_inference_jobs
```

Check queue messages:

```bash
aws sqs get-queue-attributes \
  --queue-url "$SQS_QUEUE_URL" \
  --attribute-names ApproximateNumberOfMessages
```

### 3. Run Consumer Locally

```bash
python consumer/app.py
```

### 4. Run Consumer with Docker

Build image:

```bash
docker build -t async-ai-consumer .
```

Run container:

```bash
docker run \
  -e AWS_REGION=us-east-1 \
  -e S3_BUCKET=async-ai-inference \
  -e SQS_QUEUE_URL="$SQS_QUEUE_URL" \
  -v ~/.aws:/root/.aws \
  async-ai-consumer
```

---

## Output

Predictions are stored in:

```
s3://async-ai-inference/final-project/predictions/
```

Example:

```json
{
  "record_id": "sample_001",
  "prediction": 1,
  "timestamp": "2026-04-30T20:00:00Z"
}
```

---

## Kubernetes Deployment

Deployment file: `k8s/deployment.yaml`

Apply deployment:

```bash
kubectl apply -f k8s/deployment.yaml
```

Scale consumers:

```bash
kubectl scale deployment async-ai-consumer --replicas=3
```

> **Note:** A Kubernetes cluster was not available in the Cloud9 environment. This configuration demonstrates how the system would scale in production.

---

## Design Decisions

### Why use SQS?

- Decouples producers and consumers
- Handles traffic spikes gracefully
- Enables retries and fault tolerance

### What happens if a consumer crashes?

- Message is not deleted
- Becomes visible again after timeout
- Another consumer retries processing

---

## Bottlenecks

- SQS polling latency
- Model loading time per worker
- Single consumer throughput

---

## Potential Improvements

- Kubernetes autoscaling (HPA)
- Batch inference support
- Monitoring and logging pipeline