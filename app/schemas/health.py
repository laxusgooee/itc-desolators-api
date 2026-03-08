from pydantic import BaseModel

class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    app_name: str
