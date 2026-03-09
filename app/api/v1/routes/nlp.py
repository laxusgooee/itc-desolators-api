from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.nlp import TicketLabel, NERAnnotation, NLPMetrics, TicketResult, TicketInput, DraftInput, DraftResponse
from app.services.nlp import NLPDataService

router = APIRouter()

@router.post("/", response_model=TicketResult)
def process_ticket(input_data: TicketInput):
    """Process custom text and return NLP analysis."""
    return NLPDataService.process_text(input_data.text)

@router.post("/draft", response_model=DraftResponse)
def generate_draft(input_data: DraftInput):
    """Generate a draft response using Groq."""
    draft = NLPDataService.llm_draft(input_data.text, input_data.category, [e.dict() for e in input_data.entities])
    return {"draft_response": draft}

@router.get("/labels", response_model=List[TicketLabel])
def get_labels():
    """Retrieve all ticket labels (classification)."""
    return NLPDataService.get_labels()

@router.get("/ner-annotations", response_model=List[NERAnnotation])
def get_ner_annotations():
    """Retrieve NER annotations for a subset of tickets."""
    return NLPDataService.get_ner_annotations()

@router.get("/metrics", response_model=NLPMetrics)
def get_metrics():
    """Retrieve NLP model performance metrics."""
    metrics = NLPDataService.get_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="NLP metrics not found")
    return metrics

@router.get("/results", response_model=List[TicketResult])
def get_results():
    """Retrieve sample LLM draft responses."""
    # Note: Returning results without drafts as per refactoring
    return NLPDataService.get_results()

@router.get("/{ticket_id}", response_model=TicketResult)
def get_ticket_result(ticket_id: str):
    """Retrieve detailed NLP results for a specific ticket."""
    result = NLPDataService.get_ticket_result(ticket_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"NLP result for ticket {ticket_id} not found")
    return result
