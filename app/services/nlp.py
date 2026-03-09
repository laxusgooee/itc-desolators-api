import os
import json
import pandas as pd
import re
import uuid
import urllib.request
from typing import List, Dict, Any, Optional
from app.core.config import settings

MODEL_PATH = os.path.join(settings.BASE_PATH, "models")

LABELS_CSV = os.path.join(MODEL_PATH, "nlp_ticket_labels.csv")
NER_JSONL = os.path.join(MODEL_PATH, "ner_annotations.jsonl")
METRICS_JSON = os.path.join(MODEL_PATH, "nlp_metrics.json")
RESULTS_JSON = os.path.join(MODEL_PATH, "nlp_results.json")



LABEL_RULES: List[tuple[str, List[str]]] = [
    ("Account", [
        r"log into my account",
        r"password is incorrect",
        r"reset my password",
        r"no longer have access to my email",
        r"update my email address",
        r"two-factor",
        r"account seems locked",
        r"can you unlock it",
        r"can't log in",
    ]),
    ("Refund", [
        r"refund order",
        r"when will i get my refund",
        r"refund.*taking too long",
        r"pending charge",
        r"charged twice",
        r"i cancelled ord-\d+",
        r"returned.*order.*when will",
    ]),
    ("Delivery", [
        r"update me on shipping",
        r"hasn't shown up",
        r"keeps showing .in transit.",
        r"tracking.*says delivered",
        r"can't find the package",
        r"courier left my parcel",
        r"it's been \d+ days",
    ]),
    ("Product Issue", [
        r"arrived scratched",
        r"want a replacement",
        r"is faulty",
        r"won't turn on",
        r"size/fit.*is wrong",
        r"doesn't match the description",
        r"missing parts",
        r"item arrived damaged",
    ]),
    ("Other", [
        r"size guide",
        r"warranty policy",
        r"discount code",
        r"ship internationally",
        r"back in stock",
    ]),
]

ORDER_RE = re.compile(r"\bORD-\d+\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
DATE_RE  = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}"
    r"|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?"
    r"|yesterday|today)\b",
    re.IGNORECASE,
)

class NLPDataService:
    @staticmethod
    def auto_label(text: str) -> str:
        t = text.lower()
        for category, patterns in LABEL_RULES:
            for pat in patterns:
                if re.search(pat, t):
                    return category
        return "Other"

    @staticmethod
    def extract_entities(text: str) -> List[Dict[str, Any]]:
        entities = []
        for pattern, label in [(ORDER_RE, "ORDER_ID"), (EMAIL_RE, "EMAIL"), (DATE_RE, "DATE")]:
            for m in pattern.finditer(text):
                entities.append({
                    "label": label,
                    "start": m.start(),
                    "end":   m.end(),
                    "text":  m.group(),
                })
        return sorted(entities, key=lambda e: e["start"])

    @staticmethod
    def build_prompt(text: str, category: str, entities: List[Dict[str, Any]]) -> str:
        ent_str = ", ".join(f"{e['label']}={e['text']}" for e in entities) or "none detected"
        return (
            f"You are a professional customer support agent for an e-commerce company.\n\n"
            f"Ticket category: {category}\n"
            f"Extracted entities: {ent_str}\n"
            f"Ticket:\n\"\"\"\n{text}\n\"\"\"\n\n"
            f"Write a concise, professional first-response email. Rules:\n"
            f"- Be empathetic and polite.\n"
            f"- Reference extracted entities naturally where relevant.\n"
            f"- If critical info is missing (e.g. no order ID for a delivery issue), ask for it.\n"
            f"- Do NOT invent or hallucinate any order details, dates, or tracking numbers.\n"
            f"- Keep the response under 120 words.\n"
            f"Reply with ONLY the draft response text."
        )

    @staticmethod
    def llm_draft(text: str, category: str, entities: List[Dict[str, Any]]) -> str:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": NLPDataService.build_prompt(text, category, entities)}],
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return data["content"][0]["text"].strip()
        except Exception as e:
            return f"[Draft unavailable: {e}]"

    @staticmethod
    def process_text(text: str) -> Dict[str, Any]:
        ticket_id = f"TKT-{uuid.uuid4().hex[:4].upper()}"
        category = NLPDataService.auto_label(text)
        entities = NLPDataService.extract_entities(text)

        return {
            "ticket_id": ticket_id,
            "text": text,
            "category": category,
            "entities": entities
        }

    @staticmethod
    def get_labels() -> List[Dict[str, Any]]:
        if not os.path.exists(LABELS_CSV):
            return []
        df = pd.read_csv(LABELS_CSV)
        return df.to_dict(orient="records")

    @staticmethod
    def get_ner_annotations() -> List[Dict[str, Any]]:
        if not os.path.exists(NER_JSONL):
            return []
        annotations = []
        with open(NER_JSONL, "r") as f:
            for line in f:
                if line.strip():
                    annotations.append(json.loads(line))
        return annotations

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        if not os.path.exists(METRICS_JSON):
            return {}
        with open(METRICS_JSON, "r") as f:
            return json.load(f)

    @staticmethod
    def get_results() -> List[Dict[str, Any]]:
        if not os.path.exists(RESULTS_JSON):
            return []
        with open(RESULTS_JSON, "r") as f:
            return json.load(f)

    @staticmethod
    def get_ticket_result(ticket_id: str) -> Optional[Dict[str, Any]]:
        # 1. Search in nlp_results.json
        results = NLPDataService.get_results()
        for res in results:
            if res.get("ticket_id") == ticket_id:
                return res
        
        # 2. Fallback to ner_annotations.jsonl
        annotations = NLPDataService.get_ner_annotations()
        for ann in annotations:
            if ann.get("ticket_id") == ticket_id:
                text = ann.get("text", "")
                category = NLPDataService.auto_label(text)
                entities = ann.get("entities", [])
                return {
                    "ticket_id": ticket_id,
                    "text": text,
                    "category": category,
                    "entities": entities,
                }
        
        return None
