from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=HealthCheckResponse)
def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
    }
