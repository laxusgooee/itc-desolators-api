from pydantic import BaseModel


class ClassificationResult(BaseModel):
    class_name: str
    confidence: float

class ItemClassification(BaseModel):
    """Schema for classification."""
    class_name: str
    confidence: float
    result: list[ClassificationResult]
