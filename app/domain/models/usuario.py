"""Entidad Usuario del dominio"""
from typing import Optional
from pydantic import BaseModel


class Usuario(BaseModel):
    """Entidad Usuario"""
    id: int
    nombre: str
    edad: int
    latitud: float
    longitud: float
    ubicacion_texto: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True