"""Rutas API para Usuarios"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime

from app.infrastructure.api.schemas.usuario_schema import (
    UsuarioResponseSchema,
    UsuarioUpdateSchema,
)
from app.infrastructure.api.schemas.partido_schema import PartidoCalendarioResponseSchema
from app.application.use_cases.obtener_calendario import ObtenerCalendarioUseCase
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/{usuario_id}", response_model=UsuarioResponseSchema)
def obtener_perfil(usuario_id: int):
    """Obtiene el perfil de un usuario"""
    repo = UsuarioRepository(db_instance)
    usuario = repo.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponseSchema)
def actualizar_usuario(usuario_id: int, usuario_update: UsuarioUpdateSchema):
    """Actualiza los datos de un usuario"""
    repo = UsuarioRepository(db_instance)
    usuario = repo.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario_update.edad is not None:
        usuario.edad = usuario_update.edad
    if usuario_update.descripcion is not None:
        usuario.descripcion = usuario_update.descripcion
    
    return repo.actualizar(usuario)


@router.get("/{usuario_id}/calendario", response_model=List[PartidoCalendarioResponseSchema])
def obtener_calendario(
    usuario_id: int,
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
):
    """Obtiene el calendario de partidos de un usuario"""
    try:
        use_case = ObtenerCalendarioUseCase()
        return use_case.execute(usuario_id, fecha_desde, fecha_hasta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))