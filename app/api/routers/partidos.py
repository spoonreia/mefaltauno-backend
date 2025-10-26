"""Rutas API para Partidos"""
from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime

from app.domain.schemas.partidos import (
    PartidoCreateSchema,
    PartidoUpdateSchema,
    PartidoResponseSchema,
    PartidoBusquedaResponseSchema,
    PartidoDetalleResponseSchema,
    TipoFutbol,
)
from app.domain.services.service_delegator import get_service_delegator
from app.infra.database.database import database_client

router = APIRouter(prefix="/partidos", tags=["Partidos"])

# Obtener delegador de servicios
service_delegator = get_service_delegator(database_client)


@router.post("/crear", response_model=PartidoResponseSchema)
def crear_partido(partido: PartidoCreateSchema, organizador_id: int = Query(...)):
    """Crea un nuevo partido"""
    service = service_delegator.get_partido_service()
    return service.crear(
        titulo=partido.titulo,
        dinero_por_persona=partido.dinero_por_persona,
        descripcion=partido.descripcion,
        fecha_hora=partido.fecha_hora,
        latitud=partido.latitud,
        longitud=partido.longitud,
        ubicacion_texto=partido.ubicacion_texto,
        capacidad_maxima=partido.capacidad_maxima,
        tipo_partido=partido.tipo_partido,
        tipo_futbol=partido.tipo_futbol.value,
        edad_minima=partido.edad_minima,
        organizador_id=organizador_id,
        contrasena=partido.contrasena,
    )


@router.put("/{partido_id}", response_model=PartidoDetalleResponseSchema)
def editar_partido(
    partido_id: int,
    partido_update: PartidoUpdateSchema,
    organizador_id: int = Query(...),
):
    """Edita un partido existente"""
    service = service_delegator.get_partido_service()
    service.actualizar(
        partido_id=partido_id,
        organizador_id=organizador_id,
        dinero_por_persona=partido_update.dinero_por_persona,
        descripcion=partido_update.descripcion,
        latitud=partido_update.latitud,
        longitud=partido_update.longitud,
        ubicacion_texto=partido_update.ubicacion_texto,
        capacidad_maxima=partido_update.capacidad_maxima,
        edad_minima=partido_update.edad_minima,
        contrasena=partido_update.contrasena,
    )
    return service.obtener_detalle(partido_id, organizador_id)


@router.delete("/{partido_id}")
def eliminar_partido(partido_id: int, organizador_id: int = Query(...)):
    """Elimina un partido"""
    service = service_delegator.get_partido_service()
    return service.eliminar(partido_id, organizador_id)


@router.get("/buscar", response_model=List[PartidoBusquedaResponseSchema])
def buscar_partidos(
    usuario_id: int = Query(...),
    titulo: Optional[str] = Query(None),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    distancia_maxima_km: float = Query(5.0, ge=0.1, le=50),
    tipo_futbol: Optional[TipoFutbol] = Query(None),
    edad_minima: Optional[int] = Query(None, ge=16, le=99),
):
    """Busca partidos disponibles"""
    service = service_delegator.get_partido_service()
    return service.buscar(
        usuario_id=usuario_id,
        titulo=titulo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        distancia_maxima_km=distancia_maxima_km,
        tipo_futbol=tipo_futbol,
        edad_minima=edad_minima,
    )


@router.get("/{partido_id}", response_model=PartidoDetalleResponseSchema)
def ver_detalle_partido(partido_id: int, usuario_id: int = Query(...)):
    """Obtiene el detalle completo de un partido"""
    service = service_delegator.get_partido_service()
    return service.obtener_detalle(partido_id, usuario_id)


@router.post("/{partido_id}/postularse")
def postularse_a_partido(
    partido_id: int,
    usuario_id: int = Query(...),
    contrasena: Optional[str] = Query(None),
):
    """Postularse a un partido"""
    service = service_delegator.get_partido_service()
    return service.postularse(partido_id, usuario_id, contrasena)


@router.post("/{partido_id}/participantes/{participacion_id}/gestionar")
def gestionar_participacion(
    partido_id: int,
    participacion_id: int,
    accion: str = Query(..., pattern="^(aprobar|rechazar|expulsar)$"),
    organizador_id: int = Query(...),
):
    """Gestiona una participación (aprobar/rechazar/expulsar)"""
    service = service_delegator.get_partido_service()
    return service.gestionar_participacion(
        partido_id, participacion_id, organizador_id, accion
    )


@router.delete("/{partido_id}/salir")
def salir_del_partido(partido_id: int, usuario_id: int = Query(...)):
    """Salir de un partido"""
    service = service_delegator.get_partido_service()
    return service.salir(partido_id, usuario_id)


@router.post("/{partido_id}/invitar")
def invitar_jugador(
    partido_id: int,
    jugador_id: int = Query(...),
    organizador_id: int = Query(...),
):
    """Invita un jugador a un partido"""
    service = service_delegator.get_partido_service()
    return service.invitar_jugador(partido_id, jugador_id, organizador_id)