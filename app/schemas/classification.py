from typing import Any

from pydantic import BaseModel


class ClassificationResult(BaseModel):
    class_name: str
    confidence: float

class ItemClassificationResponse(BaseModel):
    """Schema for classification."""
    class_name: str
    confidence: float
    predictions: list[ClassificationResult]

class ModelClassesResponse(BaseModel):
    """List of class labels known by the model."""
    classes: list[str]

class ModelMetricsResponse(BaseModel):
    """Metrics of the model"""
    test_accuracy: float
    test_loss: float
    epochs_run: int
    class_weights: dict[str, float]
    classification_report: dict[str, Any]
    confusion_matrix: list[list[int]]
