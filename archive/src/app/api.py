# src/app/api.py
import json
import joblib
import numpy as np
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class PredictionRequest(BaseModel):
    features: list[float]


def create_app(
    model_path: str = "models/model.pkl",
    metadata_path: str = "models/metadata.json",
):
    """
    Creates a FastAPI app that serves predictions for the breast cancer model
    and exposes model metadata.
    """

    if not Path(model_path).exists():
        raise RuntimeError(
            f"Model file not found at '{model_path}'. "
            "Train the model first by running the DAG."
        )

    if not Path(metadata_path).exists():
        raise RuntimeError(
            f"Metadata file not found at '{metadata_path}'. "
            "Train the model first by running the DAG."
        )

    model = joblib.load(model_path)

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    app = FastAPI(title="Breast Cancer Model API")

    @app.get("/")
    def root():
        return {
            "message": "Breast cancer model is ready for inference!"
        }

    @app.get("/model/info")
    def model_info():
        return metadata

    @app.post("/predict")
    def predict(request: PredictionRequest):
        try:
            X = np.array([request.features])
            prediction = int(model.predict(X)[0])
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "prediction": prediction
        }

    return app