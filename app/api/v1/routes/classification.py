"""
Classification route — POST /classify

Accepts a plant image upload and returns the predicted species + confidence.
"""

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.classification import ItemClassification
from app.services.classification import ClassificationService

router = APIRouter()

@router.post("/classify", response_model=ItemClassification)
async def classify_image(file: UploadFile = File(...)):
    """
    Upload a plant image (JPEG / PNG) and get back:
    - **class_name**: predicted plant species
    - **confidence**: model confidence (0–1)
    """
    # ── Validate content type ─────────────────────────────────────────────────
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(
            status_code=415,
            detail="Unsupported media type. Upload a JPEG or PNG image.",
        )

    # ── Read & decode image ───────────────────────────────────────────────────
    raw = await file.read()
    nparr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    # ── Pre-process: resize → BGR→RGB → normalise ─────────────────────────────
    img = cv2.resize(img, (128, 128))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype("float32") / 255.0

    # ── Predict ───────────────────────────────────────────────────────────────
    try:
        result = ClassificationService.predict(img)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return result

