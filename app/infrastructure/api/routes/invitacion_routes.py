"""Rutas API para Invitaciones"""
from fastapi import APIRouter, Query, HTTPException
from typing import List

from app.infrastructure.database.database import database_client  # ← IMPORTAR
from app.infrastructure.api.schemas.invitacion_schema import InvitacionResponseSchema
from app.application.use_cases.responder_invitacion import ResponderInvitacionUseCase
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.invitacion_repository import InvitacionRepository
from app.domain.enums.estado import EstadoInvitacion

router = APIRouter(prefix="/invitaciones", tags=["Invitaciones"])


@router.get("/usuarios/{usuario_id}", response_model=List[InvitacionResponseSchema])
def obtener_invitaciones(usuario_id: int):
    """Obtiene las invitaciones pendientes de un usuario"""
    usuario_repo = UsuarioRepository(database_client)
    usuario = usuario_repo.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    invitacion_repo = InvitacionRepository(database_client)
    invitaciones = invitacion_repo.obtener_por_jugador(usuario_id, EstadoInvitacion.PENDIENTE)

    return invitaciones


@router.post("/{invitacion_id}/responder")
def responder_invitacion(
    invitacion_id: int,
    aceptar: bool = Query(...),
    usuario_id: int = Query(...),
):
    """Responde a una invitación (aceptar o rechazar)"""
    try:
        use_case = ResponderInvitacionUseCase(database_client)
        return use_case.execute(invitacion_id, usuario_id, aceptar)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))