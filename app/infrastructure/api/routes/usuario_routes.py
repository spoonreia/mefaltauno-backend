"""Rutas API para Usuarios"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from app.infrastructure.database.database import database_client
from app.infrastructure.api.schemas.usuario_schema import (
    UsuarioResponseSchema,
    UsuarioUpdateSchema,
    JugadorDisponibleResponseSchema,
)
from app.infrastructure.api.schemas.partido_schema import PartidoCalendarioResponseSchema
from app.application.use_cases.obtener_calendario import ObtenerCalendarioUseCase
from app.application.use_cases.actualizar_postulacion import ActualizarPostulacionUseCase
from app.application.use_cases.buscar_jugadores import BuscarJugadoresDisponiblesUseCase
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.domain.enums.estado import Genero, Posicion

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ============ RUTAS ESPECÍFICAS PRIMERO (ANTES DE LAS RUTAS CON {usuario_id}) ============

@router.get("/buscar-disponibles", response_model=List[JugadorDisponibleResponseSchema])
def buscar_jugadores_disponibles(
    organizador_id: int = Query(..., description="ID del organizador que busca jugadores"),
    genero: Optional[Genero] = Query(None, description="Filtrar por género"),
    posicion: Optional[Posicion] = Query(None, description="Filtrar por posición"),
    ubicacion_texto: Optional[str] = Query(None, description="Filtrar por texto de ubicación (búsqueda parcial)"),
    distancia_maxima_km: float = Query(10.0, ge=0.1, le=100, description="Distancia máxima en kilómetros"),
):
    """
    Busca jugadores disponibles que estén postulados para ser invitados a partidos

    Retorna lista de jugadores ordenados por distancia (más cercanos primero)
    """
    try:
        use_case = BuscarJugadoresDisponiblesUseCase(database_client)
        return use_case.execute(
            organizador_id=organizador_id,
            genero=genero,
            posicion=posicion,
            ubicacion_texto=ubicacion_texto,
            distancia_maxima_km=distancia_maxima_km,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ RUTAS CON {usuario_id} AL FINAL ============

@router.get("/{usuario_id}", response_model=UsuarioResponseSchema)
def obtener_perfil(usuario_id: int):
    """Obtiene el perfil completo de un usuario"""
    repo = UsuarioRepository(database_client)
    usuario = repo.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponseSchema)
def actualizar_usuario(usuario_id: int, usuario_update: UsuarioUpdateSchema):
    repo = UsuarioRepository(database_client)
    usuario = repo.obtener_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario_actualizado = usuario.model_copy(
        update=usuario_update.model_dump(exclude_unset=True)
    )

    return repo.actualizar(usuario_actualizado)


@router.get("/{usuario_id}/calendario", response_model=List[PartidoCalendarioResponseSchema])
def obtener_calendario(
    usuario_id: int,
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
):
    """Obtiene el calendario de partidos de un usuario"""
    try:
        use_case = ObtenerCalendarioUseCase(database_client)
        return use_case.execute(usuario_id, fecha_desde, fecha_hasta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{usuario_id}/postulacion")
def actualizar_postulacion(
    usuario_id: int,
    activo: bool = Query(..., description="True para postularse, False para despostularse"),
):
    """
    Activa o desactiva la postulación del usuario para aparecer en búsquedas de jugadores

    - **activo=true**: El usuario se postula y aparece en las búsquedas
    - **activo=false**: El usuario se despostula y NO aparece en las búsquedas
    """
    try:
        use_case = ActualizarPostulacionUseCase(database_client)
        return use_case.execute(usuario_id, activo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))