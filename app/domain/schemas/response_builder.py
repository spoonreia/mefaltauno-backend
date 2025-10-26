"""Builder para respuestas genéricas"""
from typing import Any, Optional, Dict
from pydantic import BaseModel


class GenericResponse(BaseModel):
    """Schema genérico de respuesta"""
    mensaje: str
    datos: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "Operación exitosa",
                "datos": {
                    "id": 1,
                    "estado": "confirmado"
                }
            }
        }


class ResponseBuilder:
    """Constructor de respuestas estandarizadas"""

    @staticmethod
    def success(mensaje: str, datos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crea respuesta de éxito"""
        response = {"mensaje": mensaje}
        if datos:
            response.update(datos)
        return response

    @staticmethod
    def error(mensaje: str, detalle: Optional[str] = None) -> Dict[str, Any]:
        """Crea respuesta de error"""
        response = {"error": mensaje}
        if detalle:
            response["detalle"] = detalle
        return response