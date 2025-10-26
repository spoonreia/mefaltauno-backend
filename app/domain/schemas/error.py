"""Schemas para errores"""
from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Schema de respuesta para errores"""
    error: str
    mensaje: str
    detalle: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "PartidoNoEncontrado",
                "mensaje": "El partido solicitado no existe",
                "detalle": "ID: 123"
            }
        }