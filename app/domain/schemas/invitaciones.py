"""Schemas Pydantic para Invitaciones"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


# ============================================
# ENUMS
# ============================================

class EstadoInvitacion(str, Enum):
    PENDIENTE = "Pendiente"
    ACEPTADA = "Aceptada"
    RECHAZADA = "Rechazada"


# ============================================
# RESPONSE SCHEMAS
# ============================================

class InvitacionResponseSchema(BaseModel):
    """Schema de respuesta para invitaciones"""
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