from fastapi import APIRouter

from app.api.v1.routes import classification, items

router = APIRouter()

router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(
    classification.router, prefix="/classification", tags=["classification"]
)

