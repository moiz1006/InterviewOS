"""Response schemas for the system/health endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
