"""Rutas API para Invitaciones"""
from fastapi import APIRouter, Query, HTTPException
from typing import List

from app.infrastructure.api.schemas.invitacion_schema import InvitacionResponseSchema
from app.application.use_cases.responder_invitacion import ResponderInvitacionUseCase
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance
from app.domain.enums.estado import EstadoInvitacion

router = APIRouter(prefix="/invitaciones", tags=["Invitaciones"])


@router.get("/usuarios/{usuario_id}", response_model=List[InvitacionResponseSchema])
def obtener_invitaciones(usuario_id: int):
    """Obtiene las invitaciones pendientes de un usuario"""
    repo = UsuarioRepository(db_instance)
    usuario = repo.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    invitaciones = [
        i for i in db_instance.invitaciones_db
        if i.jugador_id == usuario_id and i.estado == EstadoInvitacion.PENDIENTE
    ]
    return invitaciones


@router.post("/{invitacion_id}/responder")
def responder_invitacion(
    invitacion_id: int,
    aceptar: bool = Query(...),
    usuario_id: int = Query(...),
):
    """Responde a una invitación (aceptar o rechazar)"""
    try:
        use_case = ResponderInvitacionUseCase()
        return use_case.execute(invitacion_id, usuario_id, aceptar)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))