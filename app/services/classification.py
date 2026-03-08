"""
Classification service — loads the trained Keras model and LabelEncoder
from pickle files and exposes a predict() and metrics() method.
"""

import json
import os
import pickle
import tempfile
from typing import Sequence, Tuple
import numpy as np
import tensorflow as tf
from app.core.config import settings


MODEL_PATH = os.path.join(settings.BASE_PATH, "models")

MODEL_PKL   = os.path.abspath(os.path.join(MODEL_PATH, "plant_model.pkl"))
ENCODER_PKL = os.path.abspath(os.path.join(MODEL_PATH, "plant_encoder.pkl"))
METRICS_JSON = os.path.abspath(os.path.join(MODEL_PATH, "plant_metrics.json"))

IMG_SIZE = 128

class ClassificationService:
    """Singleton-style service: model is loaded once on first access."""

    _model = None
    _encoder = None

    @classmethod
    def _load(cls):
        if cls._model is None:
            # ── Load model ────────────────────────────────────────────────────
            if not os.path.exists(MODEL_PKL):
                raise FileNotFoundError(
                    f"Model pickle not found at {MODEL_PKL}. "
                    "Run models/classification/train.py first."
                )
            with open(MODEL_PKL, "rb") as f:
                model_bytes = pickle.load(f)

            # Write bytes to a temp .keras file and reload
            with tempfile.NamedTemporaryFile(suffix=".keras", delete=False) as tmp:
                tmp.write(model_bytes)
                tmp_path = tmp.name
            cls._model = tf.keras.models.load_model(tmp_path)
            os.unlink(tmp_path)

            # ── Load encoder ──────────────────────────────────────────────────
            with open(ENCODER_PKL, "rb") as f:
                cls._encoder = pickle.load(f)

    @classmethod
    def predict(cls, image_array: np.ndarray) -> dict:
        """
        Predict the plant species for a single pre-processed image.

        Parameters
        ----------
        image_array : np.ndarray
            Shape (128, 128, 3), float32, values in [0, 1].

        Returns
        -------
        dict with keys:
            class_name  : str   – predicted species label
            confidence  : float – softmax probability of the top class
            predictions : list  – all classes ranked by confidence
        """
        cls._load()

        probs = cls._model.predict(image_array[np.newaxis, ...], verbose=0)[0]

        ranked = sorted(
            [
                {"class_name": cls._encoder.classes_[i], "confidence": round(float(probs[i]), 4)}
                for i in range(len(probs))
            ],
            key=lambda x: x["confidence"],
            reverse=True,
        )

        return {
            "class_name":  ranked[0]["class_name"],
            "confidence":  ranked[0]["confidence"],
            "predictions": ranked,
        }

    @classmethod
    def classes(cls) -> list[str]:
        """Return the list of class names known by the encoder."""
        cls._load()
        return cls._encoder.classes_.tolist()

    @classmethod
    def metrics(
        cls
    ) -> dict:
        """
        Get model metrics


        Returns
        -------
        dict with keys:
            accuracy          : float
            classification_report : dict  (per-class precision/recall/f1 + averages)
        """
        if not os.path.exists(METRICS_JSON):
            raise FileNotFoundError(
                f"Metrics file not found at {METRICS_JSON}. "
                "Run models/classification/train.py first."
            )

        with open(METRICS_JSON, "r") as f:
            data = json.load(f)

        return data
