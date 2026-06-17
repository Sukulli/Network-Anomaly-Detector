from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.schemas import PredictionRequest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "model.pkl"
DEFAULT_METADATA_PATH = PROJECT_ROOT / "models" / "metadata.json"
DEFAULT_THRESHOLD = 0.5


class ModelService:
    def __init__(
        self,
        model_path: Path = DEFAULT_MODEL_PATH,
        metadata_path: Path = DEFAULT_METADATA_PATH,
    ) -> None:
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = None
        self.metadata: dict[str, Any] = {}
        self.feature_columns: list[str] = []
        self.threshold = DEFAULT_THRESHOLD

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        self.model = joblib.load(self.model_path)
        self.metadata = self._load_metadata()
        self.threshold = self._load_threshold()
        self.feature_columns = [
            *self.metadata.get("numeric_features", []),
            *self.metadata.get("categorical_features", []),
        ]

        if not self.feature_columns:
            raise ValueError("Model metadata does not define input feature columns.")

    def is_loaded(self) -> bool:
        return self.model is not None

    def predict(self, payload: PredictionRequest) -> dict[str, Any]:
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        features = payload.model_dump()
        row = pd.DataFrame([{column: features[column] for column in self.feature_columns}])
        attack_probability = float(self.model.predict_proba(row)[0, 1])
        prediction = int(attack_probability >= self.threshold)

        return {
            "prediction": prediction,
            "prediction_label": "attack" if prediction == 1 else "normal",
            "attack_probability": attack_probability,
            "threshold": self.threshold,
            "model_name": self.metadata.get("primary_model_display_name", "unknown"),
        }

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.is_loaded() else "degraded",
            "model_loaded": self.is_loaded(),
            "model_name": self.metadata.get("primary_model_display_name"),
            "generated_at": self.metadata.get("generated_at"),
            "threshold": self.threshold if self.is_loaded() else None,
        }

    def _load_metadata(self) -> dict[str, Any]:
        if not self.metadata_path.exists():
            return {}

        return json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def _load_threshold(self) -> float:
        env_threshold = os.getenv("NETSHIELD_THRESHOLD")
        if env_threshold is not None:
            return float(env_threshold)

        return float(self.metadata.get("decision_threshold", DEFAULT_THRESHOLD))


model_service = ModelService()
