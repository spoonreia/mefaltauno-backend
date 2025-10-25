"""Schemas Pydantic para la API de Usuarios"""
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.enums.estado import Genero, Posicion


class UsuarioResponseSchema(BaseModel):
    """Schema de respuesta para usuarios"""
    id: int
    nombre: str
    edad: int
    latitud: float
    longitud: float
    ubicacion_texto: str
    descripcion: Optional[str] = None
    genero: Genero
    posicion: Posicion
    postulado: bool

    class Config:
        from_attributes = True


class UsuarioUpdateSchema(BaseModel):
    """Schema para actualizar usuario"""
    edad: Optional[int] = Field(None, ge=16, le=99)
    descripcion: Optional[str] = Field(None, max_length=500)
    genero: Optional[Genero] = None
    posicion: Optional[Posicion] = None


class JugadorDisponibleResponseSchema(BaseModel):
    id: int
    nombre: str
    posicion: Posicion
    genero: Genero
    edad: int
    ubicacion_texto: str
    distancia_km: float

    class Config:
        from_attributes = True