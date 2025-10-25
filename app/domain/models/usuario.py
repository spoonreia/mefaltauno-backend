"""Entidad Usuario del dominio"""
from typing import Optional
from pydantic import BaseModel
from app.domain.enums.estado import Genero, Posicion


class Usuario(BaseModel):
    """Entidad Usuario"""
    id: int
    nombre: str
    edad: int
    latitud: float
    longitud: float
    ubicacion_texto: str
    descripcion: Optional[str] = None
    genero: Genero
    posicion: Posicion
    postulado: bool = False

    class Config:
        from_attributes = True