"""Rutas API para Partidos - COMPLETAS"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime

from app.infrastructure.api.schemas.partido_schema import (
    PartidoCreateSchema,
    PartidoUpdateSchema,
    PartidoResponseSchema,
    PartidoBusquedaResponseSchema,
    PartidoDetalleResponseSchema,
    PartidoCalendarioResponseSchema,
)
from app.application.use_cases.crear_partido import CrearPartidoUseCase
from app.application.use_cases.editar_partido import EditarPartidoUseCase
from app.application.use_cases.eliminar_partido import EliminarPartidoUseCase
from app.application.use_cases.buscar_partidos import BuscarPartidosUseCase
from app.application.use_cases.postularse_partido import PostularsePartidoUseCase
from app.application.use_cases.gestionar_participacion import GestionarParticipacionUseCase
from app.application.use_cases.salir_partido import SalirPartidoUseCase
from app.application.use_cases.obtener_calendario import ObtenerCalendarioUseCase
from app.application.use_cases.ver_detalle_partido import VerDetallePartidoUseCase
from app.application.use_cases.invitar_jugador import InvitarJugadorUseCase
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PermisosDenegadosException,
    CapacidadInvalidaException,
    PartidoCompletoException,
    ContrasenaIncorrectaException,
)
from app.domain.enums.estado import TipoFutbol

router = APIRouter(prefix="/partidos", tags=["Partidos"])


@router.post("/crear", response_model=PartidoResponseSchema)
def crear_partido(partido: PartidoCreateSchema, organizador_id: int = Query(...)):
    """Crea un nuevo partido"""
    try:
        use_case = CrearPartidoUseCase()
        partido_creado = use_case.execute(
            titulo=partido.titulo,
            dinero_por_persona=partido.dinero_por_persona,
            descripcion=partido.descripcion,
            fecha_hora=partido.fecha_hora,
            latitud=partido.latitud,
            longitud=partido.longitud,
            ubicacion_texto=partido.ubicacion_texto,
            capacidad_maxima=partido.capacidad_maxima,
            tipo_partido=partido.tipo_partido,
            tipo_futbol=partido.tipo_futbol,
            edad_minima=partido.edad_minima,
            organizador_id=organizador_id,
            contrasena=partido.contrasena,
        )
        return partido_creado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{partido_id}", response_model=PartidoDetalleResponseSchema)
def editar_partido(
    partido_id: int,
    partido_update: PartidoUpdateSchema,
    organizador_id: int = Query(...),
):
    """Edita un partido existente"""
    try:
        use_case = EditarPartidoUseCase()
        partido_actualizado = use_case.execute(
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
        # Convertir a detalle
        detalle_use_case = VerDetallePartidoUseCase()
        return detalle_use_case.execute(partido_id, organizador_id)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CapacidadInvalidaException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{partido_id}")
def eliminar_partido(partido_id: int, organizador_id: int = Query(...)):
    """Elimina un partido"""
    try:
        use_case = EliminarPartidoUseCase()
        return use_case.execute(partido_id, organizador_id)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    try:
        use_case = BuscarPartidosUseCase()
        return use_case.execute(
            usuario_id=usuario_id,
            titulo=titulo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            distancia_maxima_km=distancia_maxima_km,
            tipo_futbol=tipo_futbol,
            edad_minima=edad_minima,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{partido_id}", response_model=PartidoDetalleResponseSchema)
def ver_detalle_partido(partido_id: int, usuario_id: int = Query(...)):
    """Obtiene el detalle completo de un partido"""
    try:
        use_case = VerDetallePartidoUseCase()
        return use_case.execute(partido_id, usuario_id)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise


@router.post("/{partido_id}/postularse")
def postularse_a_partido(
    partido_id: int,
    usuario_id: int = Query(...),
    contrasena: Optional[str] = Query(None),
):
    """Postularse a un partido"""
    try:
        use_case = PostularsePartidoUseCase()
        return use_case.execute(partido_id, usuario_id, contrasena)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PartidoCompletoException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ContrasenaIncorrectaException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== APROBAR PARTICIPACIÓN ====================
@router.post("/{partido_id}/participantes/{participacion_id}/aprobar")
def aprobar_participacion(
    partido_id: int,
    participacion_id: int,
    organizador_id: int = Query(...),
):
    """Aprueba una participación pendiente"""
    try:
        use_case = GestionarParticipacionUseCase()
        return use_case.execute(partido_id, participacion_id, organizador_id, "aprobar")
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except PartidoCompletoException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== RECHAZAR PARTICIPACIÓN ====================
@router.post("/{partido_id}/participantes/{participacion_id}/rechazar")
def rechazar_participacion(
    partido_id: int,
    participacion_id: int,
    organizador_id: int = Query(...),
):
    """Rechaza una participación pendiente"""
    try:
        use_case = GestionarParticipacionUseCase()
        return use_case.execute(partido_id, participacion_id, organizador_id, "rechazar")
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== EXPULSAR PARTICIPANTE ====================
@router.delete("/{partido_id}/participantes/{participacion_id}/expulsar")
def expulsar_participante(
    partido_id: int,
    participacion_id: int,
    organizador_id: int = Query(...),
):
    """Expulsa un participante confirmado del partido"""
    try:
        use_case = GestionarParticipacionUseCase()
        return use_case.execute(partido_id, participacion_id, organizador_id, "expulsar")
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== GESTIONAR PARTICIPACIÓN (GENÉRICO) ====================
@router.post("/{partido_id}/participantes/{participacion_id}/gestionar")
def gestionar_participacion(
    partido_id: int,
    participacion_id: int,
    accion: str = Query(..., pattern="^(aprobar|rechazar|expulsar)$"),
    organizador_id: int = Query(...),
):
    """Gestiona una participación (aprobar/rechazar/expulsar)"""
    try:
        use_case = GestionarParticipacionUseCase()
        return use_case.execute(partido_id, participacion_id, organizador_id, accion)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except PartidoCompletoException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== SALIR DEL PARTIDO ====================
@router.delete("/{partido_id}/salir")
def salir_del_partido(partido_id: int, usuario_id: int = Query(...)):
    """Salir de un partido"""
    try:
        use_case = SalirPartidoUseCase()
        return use_case.execute(partido_id, usuario_id)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== INVITAR JUGADOR ====================
@router.post("/{partido_id}/invitar")
def invitar_jugador(
    partido_id: int,
    jugador_id: int = Query(...),
    organizador_id: int = Query(...),
):
    """Invita un jugador a un partido"""
    try:
        use_case = InvitarJugadorUseCase()
        return use_case.execute(partido_id, jugador_id, organizador_id)
    except PartidoNoEncontradoException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))