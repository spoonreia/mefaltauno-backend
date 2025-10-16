"""Entidad Participacion del dominio"""
from datetime import datetime
from pydantic import BaseModel
from app.domain.enums.estado import EstadoParticipacion


class Participacion(BaseModel):
    """Entidad Participacion"""
    id: int
    partido_id: int
    jugador_id: int
    jugador_nombre: str
    estado: EstadoParticipacion
    fecha_postulacion: datetime

    class Config:
        from_attributes = True