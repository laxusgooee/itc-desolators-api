from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TicketInput(BaseModel):
    text: str

class TicketLabel(BaseModel):
    ticket_id: str
    category: str

class Entity(BaseModel):
    label: str
    start: int
    end: int
    text: str

class NERAnnotation(BaseModel):
    ticket_id: str
    text: str
    entities: List[Entity]

class NLPMetrics(BaseModel):
    model_name: str
    test_accuracy: float
    val_accuracy: float
    epochs: int
    train_size: int
    val_size: int
    test_size: int
    classes: List[str]
    classification_report: Dict[str, Any]
    confusion_matrix: List[List[int]]
    ner_summary: Optional[Dict[str, Any]] = None

class TicketResult(BaseModel):
    ticket_id: str
    text: str
    category: str
    entities: List[Entity]

class DraftInput(BaseModel):
    text: str
    category: str
    entities: List[Entity]

class DraftResponse(BaseModel):
    draft_response: str
