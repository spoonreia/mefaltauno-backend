"""Servicio de dominio para la lógica de negocio de partidos"""
from datetime import datetime, timedelta
from typing import Optional
from app.domain.models.partido import Partido
from app.domain.enums.estado import TipoPartido, EstadoParticipacion
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PermisosDenegadosException,
    CapacidadInvalidaException,
)


class PartidoService:
    """Servicio de dominio para partidos"""

    @staticmethod
    def validar_organizador(partido: Partido, usuario_id: int) -> None:
        """Valida que el usuario sea el organizador del partido"""
        if partido.organizador_id != usuario_id:
            raise PermisosDenegadosException(
                "Solo el organizador puede realizar esta acción"
            )

    @staticmethod
    def validar_capacidad(capacidad_nueva: int, confirmados: int) -> None:
        """Valida que la nueva capacidad sea válida"""
        if capacidad_nueva < confirmados:
            raise CapacidadInvalidaException(
                f"La capacidad no puede ser menor a los jugadores confirmados ({confirmados})"
            )

    @staticmethod
    def puede_eliminar_partido(partido: Partido) -> bool:
        """Verifica si un partido puede ser eliminado (más de 24h de anticipación)"""
        tiempo_restante = partido.fecha_hora - datetime.now()
        return tiempo_restante.total_seconds() >= 24 * 3600

    @staticmethod
    def gestionar_privacidad(
        partido: Partido, contrasena: Optional[str]
    ) -> Partido:
        """Gestiona el cambio de privacidad del partido"""
        if contrasena is not None:
            if contrasena == "":
                # Quitar contraseña (hacer público)
                partido.tipo_partido = TipoPartido.PUBLICO
                partido.contrasena = None
            else:
                # Agregar o cambiar contraseña (hacer privado)
                partido.tipo_partido = TipoPartido.PRIVADO
                partido.contrasena = contrasena
        return partido