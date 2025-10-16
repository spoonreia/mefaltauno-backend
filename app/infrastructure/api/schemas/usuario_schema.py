"""Schemas Pydantic para la API de Usuarios"""
from typing import Optional
from pydantic import BaseModel, Field


class UsuarioResponseSchema(BaseModel):
    """Schema de respuesta para usuarios"""
    id: int
    nombre: str
    edad: int
    latitud: float
    longitud: float
    ubicacion_texto: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioUpdateSchema(BaseModel):
    """Schema para actualizar usuario"""
    edad: Optional[int] = Field(None, ge=16, le=99)
    descripcion: Optional[str] = Field(None, max_length=500)