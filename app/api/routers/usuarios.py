"""Rutas API para Usuarios"""
from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime

from app.domain.schemas.usuarios import (
    UsuarioResponseSchema,
    UsuarioUpdateSchema,
    JugadorDisponibleResponseSchema,
    Genero,
    Posicion,
)
from app.domain.schemas.partidos import PartidoCalendarioResponseSchema
from app.domain.services.service_delegator import get_service_delegator
from app.infra.database.database import database_client

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Obtener delegador de servicios
service_delegator = get_service_delegator(database_client)


# ============================================
# RUTAS ESPECÍFICAS (ANTES DE LAS RUTAS CON {usuario_id})
# ============================================

@router.get("/buscar-disponibles", response_model=List[JugadorDisponibleResponseSchema])
def buscar_jugadores_disponibles(
    organizador_id: int = Query(..., description="ID del organizador que busca jugadores"),
    genero: Optional[Genero] = Query(None, description="Filtrar por género"),
    posicion: Optional[Posicion] = Query(None, description="Filtrar por posición"),
    ubicacion_texto: Optional[str] = Query(None, description="Filtrar por texto de ubicación"),
    distancia_maxima_km: float = Query(10.0, ge=0.1, le=100, description="Distancia máxima en km"),
):
    """
    Busca jugadores disponibles que estén postulados para ser invitados a partidos.
    Retorna lista de jugadores ordenados por distancia (más cercanos primero).
    """
    service = service_delegator.get_usuario_service()
    return service.buscar_jugadores_disponibles(
        organizador_id=organizador_id,
        genero=genero,
        posicion=posicion,
        ubicacion_texto=ubicacion_texto,
        distancia_maxima_km=distancia_maxima_km,
    )


# ============================================
# RUTAS CON PARÁMETRO {usuario_id}
# ============================================

@router.get("/{usuario_id}", response_model=UsuarioResponseSchema)
def obtener_perfil(usuario_id: int):
    """Obtiene el perfil completo de un usuario"""
    service = service_delegator.get_usuario_service()
    return service.obtener_perfil(usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponseSchema)
def actualizar_usuario(usuario_id: int, usuario_update: UsuarioUpdateSchema):
    """Actualiza la información de un usuario"""
    service = service_delegator.get_usuario_service()
    usuario_data = usuario_update.model_dump(exclude_unset=True)

    # Convertir enums a strings para la base de datos
    if 'genero' in usuario_data and usuario_data['genero']:
        usuario_data['genero'] = usuario_data['genero'].value
    if 'posicion' in usuario_data and usuario_data['posicion']:
        usuario_data['posicion'] = usuario_data['posicion'].value
    if 'fechaNac' in usuario_data:
        usuario_data['fecha_nacimiento'] = usuario_data.pop('fechaNac')

    service.actualizar(usuario_id, usuario_data)
    return service.obtener_perfil(usuario_id)


@router.get("/{usuario_id}/calendario", response_model=List[PartidoCalendarioResponseSchema])
def obtener_calendario(
    usuario_id: int,
    fecha_desde: Optional[datetime] = Query(None, description="Fecha de inicio del calendario"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha de fin del calendario"),
):
    """
    Obtiene el calendario de partidos confirmados de un usuario.
    Por defecto muestra los próximos 30 días desde hoy.
    """
    service = service_delegator.get_usuario_service()
    return service.obtener_calendario(usuario_id, fecha_desde, fecha_hasta)


@router.post("/{usuario_id}/postulacion")
def actualizar_postulacion(
    usuario_id: int,
    activo: bool = Query(..., description="True para postularse, False para despostularse"),
):
    """
    Activa o desactiva la postulación del usuario para aparecer en búsquedas de jugadores.

    - **activo=true**: El usuario se postula y aparece en las búsquedas
    - **activo=false**: El usuario se despostula y NO aparece en las búsquedas
    """
    service = service_delegator.get_usuario_service()
    return service.actualizar_postulacion(usuario_id, activo)