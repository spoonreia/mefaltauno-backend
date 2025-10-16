"""Entidad Partido del dominio"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.domain.enums.estado import TipoPartido, TipoFutbol, EstadoPartido


class Partido(BaseModel):
    """Entidad Partido"""
    id: int
    titulo: str
    dinero_por_persona: int
    descripcion: Optional[str]
    fecha_hora: datetime
    latitud: float
    longitud: float
    ubicacion_texto: str
    capacidad_maxima: int
    organizador_id: int
    tipo_partido: TipoPartido
    tipo_futbol: TipoFutbol
    edad_minima: int
    estado: EstadoPartido
    contrasena: Optional[str] = None

    class Config:
        from_attributes = True