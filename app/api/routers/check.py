"""Router para health checks"""
from fastapi import APIRouter

from app.domain.schemas.check import HealthCheckResponse
from app.utils.config import settings

router = APIRouter(tags=["Health Check"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "ok",
        "service": "me-falta-uno-api",
        "version": settings.API_VERSION
    }