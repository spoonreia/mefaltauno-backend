"""Schemas Pydantic para la API de Usuarios"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.enums.estado import Genero, Posicion


class UsuarioResponseSchema(BaseModel):
    """Schema de respuesta para usuarios"""
    id: int
    posicion: Posicion
    nombre: str
    edad: int
    fechaNac: date
    ubicacion_texto: str
    descripcion: Optional[str] = None
    genero: Genero
    latitud: float
    longitud: float

    class Config:
        from_attributes = True


class UsuarioUpdateSchema(BaseModel):
    """Schema para actualizar usuario"""
    nombre: Optional[str] = None
    fechaNac: Optional[date] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    ubicacion_texto: Optional[str] = None
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