"""Schemas para health checks"""
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Schema de respuesta para health check"""
    status: str
    service: str
    version: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "service": "me-falta-uno-api",
                "version": "2.0.0"
            }
        }