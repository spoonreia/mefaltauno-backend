"""Schemas Pydantic para Partidos"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ============================================
# ENUMS
# ============================================

class TipoPartido(str, Enum):
    PUBLICO = "Publico"
    PRIVADO = "Privado"


class TipoFutbol(str, Enum):
    FUTBOL_5 = "Futbol 5"
    FUTBOL_7 = "Futbol 7"
    FUTBOL_11 = "Futbol 11"


class EstadoPartido(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"
    FINALIZADO = "Finalizado"


class EstadoParticipacion(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADO = "Confirmado"
    RECHAZADO = "Rechazado"
    CANCELADO = "Cancelado"


# ============================================
# REQUEST SCHEMAS
# ============================================

class PartidoCreateSchema(BaseModel):
    """Schema para crear un partido"""
    titulo: str = Field(..., min_length=3, max_length=100)
    dinero_por_persona: int
    descripcion: Optional[str] = None
    fecha_hora: datetime
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    ubicacion_texto: str
    capacidad_maxima: int = Field(..., ge=2, le=22)
    tipo_partido: TipoPartido
    tipo_futbol: TipoFutbol
    edad_minima: int = Field(..., ge=16, le=99)
    contrasena: Optional[str] = None


class PartidoUpdateSchema(BaseModel):
    """Schema para actualizar un partido"""
    dinero_por_persona: Optional[int] = None
    descripcion: Optional[str] = Field(None, max_length=500)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    ubicacion_texto: Optional[str] = None
    capacidad_maxima: Optional[int] = Field(None, ge=2, le=22)
    edad_minima: Optional[int] = Field(None, ge=16, le=99)
    contrasena: Optional[str] = None


# ============================================
# RESPONSE SCHEMAS
# ============================================

class PartidoResponseSchema(BaseModel):
    """Schema de respuesta básico para partidos"""
    id: int
    titulo: str
    dinero_por_persona: int
    descripcion: Optional[str]
    fecha_hora: datetime
    ubicacion_texto: str
    capacidad_maxima: int
    tipo_partido: TipoPartido
    tipo_futbol: TipoFutbol

    class Config:
        from_attributes = True


class PartidoBusquedaResponseSchema(BaseModel):
    """Schema de respuesta para búsqueda de partidos"""
    id: int
    titulo: str
    dinero_por_persona: int
    descripcion: Optional[str]
    fecha_hora: datetime
    latitud: float
    longitud: float
    ubicacion_texto: str
    capacidad_maxima: int
    jugadores_confirmados: int
    organizador_id: int
    organizador_nombre: str
    tipo_partido: TipoPartido
    tipo_futbol: TipoFutbol
    edad_minima: int
    estado: EstadoPartido
    tiene_cupo: bool
    distancia_km: float

    class Config:
        from_attributes = True


class ParticipacionSchema(BaseModel):
    """Schema para participaciones"""
    id: int
    partido_id: int
    jugador_id: int
    jugador_nombre: str
    estado: EstadoParticipacion
    fecha_postulacion: datetime

    class Config:
        from_attributes = True


class PartidoDetalleResponseSchema(BaseModel):
    """Schema de respuesta detallado para un partido"""
    id: int
    titulo: str
    dinero_por_persona: int
    descripcion: Optional[str]
    fecha_hora: datetime
    latitud: float
    longitud: float
    ubicacion_texto: str
    capacidad_maxima: int
    jugadores_confirmados: int
    jugadores_pendientes: int
    organizador_id: int
    organizador_nombre: str
    tipo_partido: TipoPartido
    tipo_futbol: TipoFutbol
    edad_minima: int
    estado: EstadoPartido
    tiene_cupo: bool
    participantes: List[ParticipacionSchema]

    class Config:
        from_attributes = True


class PartidoCalendarioResponseSchema(BaseModel):
    """Schema para partidos en el calendario"""
    id: int
    titulo: str
    fecha_hora: datetime
    ubicacion_texto: str
    es_organizador: bool
    jugadores_confirmados: int
    capacidad_maxima: int
    tipo_partido: TipoPartido

    class Config:
        from_attributes = True