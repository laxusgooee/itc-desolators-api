"""
Classification routes:
  POST /classify          – predict a single image
  GET  /metrics/classes   – list all class labels the model knows
  POST /metrics           – upload a ZIP of labelled images → classification report
"""

import io
import zipfile

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.classification import (
    ModelClassesResponse,
    ModelMetricsResponse,
    ItemClassificationResponse,
)
from app.services.classification import ClassificationService

router = APIRouter()

IMG_SIZE = 128
ALLOWED_TYPES = ("image/jpeg", "image/png", "image/jpg")
ALLOWED_EXTS  = {".jpg", ".jpeg", ".png"}


def _decode_image(raw: bytes) -> np.ndarray | None:
    """Decode raw image bytes → (128,128,3) float32 array or None on failure."""
    nparr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img.astype("float32") / 255.0


# ── Single-image prediction ────────────────────────────────────────────────────

@router.post("/classify", response_model=ItemClassificationResponse)
async def classify_image(file: UploadFile = File(...)):
    """
    Upload a plant image (JPEG / PNG) and get back:
    - **class_name**: predicted plant species
    - **confidence**: model confidence (0–1)
    - **predictions**: all classes ranked by confidence
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported media type. Upload a JPEG or PNG image.",
        )

    raw = await file.read()
    img = _decode_image(raw)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    try:
        result = ClassificationService.predict(img)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return result


# ── Metrics ───────────────────────────────────────────────────────────────────

@router.get("/metrics/classes", response_model=ModelClassesResponse)
def get_classes():
    """Return the list of plant classes the model was trained on."""
    try:
        return {"classes": ClassificationService.classes()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/metrics", response_model=ModelMetricsResponse)
async def compute_metrics():
    """
   Returns metrics of the model.
    """
    
    try:
        result = ClassificationService.metrics()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return result
