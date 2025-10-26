"""Rutas API para Invitaciones"""
from fastapi import APIRouter, Query
from typing import List

from app.domain.schemas.invitaciones import InvitacionResponseSchema, EstadoInvitacion
from app.domain.services.service_delegator import get_service_delegator
from app.infra.database.database import database_client

router = APIRouter(prefix="/invitaciones", tags=["Invitaciones"])

# Obtener delegador de servicios
service_delegator = get_service_delegator(database_client)


@router.get("/usuarios/{usuario_id}", response_model=List[InvitacionResponseSchema])
def obtener_invitaciones(usuario_id: int):
    """Obtiene las invitaciones pendientes de un usuario"""
    service = service_delegator.get_invitacion_service()
    return service.obtener_por_usuario(usuario_id, EstadoInvitacion.PENDIENTE)


@router.post("/{invitacion_id}/responder")
def responder_invitacion(
    invitacion_id: int,
    aceptar: bool = Query(...),
    usuario_id: int = Query(...),
):
    """Responde a una invitación (aceptar o rechazar)"""
    service = service_delegator.get_invitacion_service()
    return service.responder(invitacion_id, usuario_id, aceptar)