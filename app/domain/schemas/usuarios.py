"""Schemas Pydantic para Usuarios"""
from datetime import date
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================
# ENUMS
# ============================================

class Genero(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    NO_DEFINIDO = "Otro"


class Posicion(str, Enum):
    ARQUERO = "Arquero"
    DEFENSA = "Defensa"
    MEDIOCAMPISTA = "Mediocampista"
    DELANTERO = "Delantero"


# ============================================
# REQUEST SCHEMAS
# ============================================

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


# ============================================
# RESPONSE SCHEMAS
# ============================================

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
    postulado: bool

    class Config:
        from_attributes = True


class JugadorDisponibleResponseSchema(BaseModel):
    """Schema para jugadores disponibles para invitar"""
    id: int
    nombre: str
    posicion: Posicion
    genero: Genero
    edad: int
    ubicacion_texto: str
    distancia_km: float

    class Config:
        from_attributes = True