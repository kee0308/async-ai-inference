import os
import json
from datetime import datetime

import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def train_model(model_dir: str = "models") -> float:
    """Train model, save artifacts, return accuracy"""

    os.makedirs(model_dir, exist_ok=True)

    # 🔹 version
    version = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 🔹 load better dataset
    data = load_breast_cancer()
    X = data.data
    y = data.target

    # 🔹 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 🔹 train
    clf = LogisticRegression(max_iter=10000)
    clf.fit(X_train, y_train)

    # 🔹 evaluate
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"[ml_pipeline.model] Accuracy: {acc:.4f}")

    # 🔹 save model
    model_path = os.path.join(model_dir, "model.pkl")
    joblib.dump(clf, model_path)

    # 🔹 save metrics
    metrics = {"accuracy": float(acc)}
    with open(os.path.join(model_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # 🔹 save metadata (IMPORTANT)
    metadata = {
        "model_version": version,
        "dataset": "breast_cancer",
        "model_type": "logistic_regression",
        "accuracy": float(acc),
    }

    with open(os.path.join(model_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[ml_pipeline.model] Saved model + metadata")

    return metadata