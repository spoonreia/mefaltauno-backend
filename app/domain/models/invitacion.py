"""Entidad Invitacion del dominio"""
from datetime import datetime
from pydantic import BaseModel
from app.domain.enums.estado import EstadoInvitacion


class Invitacion(BaseModel):
    """Entidad Invitacion"""
    id: int
    partido_id: int
    partido_titulo: str
    partido_fecha_hora: datetime
    partido_ubicacion: str
    jugador_id: int
    estado: EstadoInvitacion
    fecha_invitacion: datetime

    class Config:
        from_attributes = True