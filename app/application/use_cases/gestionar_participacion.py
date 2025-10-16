"""Caso de uso: Gestionar Participación (aprobar/rechazar/expulsar)"""
from app.domain.enums.estado import EstadoParticipacion
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PermisosDenegadosException,
    PartidoCompletoException,
)
from app.domain.services.partido_service import PartidoService
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class GestionarParticipacionUseCase:
    """Caso de uso para gestionar participaciones"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.partido_service = PartidoService()

    def execute(
        self,
        partido_id: int,
        participacion_id: int,
        organizador_id: int,
        accion: str,  # 'aprobar', 'rechazar', 'expulsar'
    ) -> dict:
        """Ejecuta el caso de uso"""

        # Validar acción
        if accion not in ['aprobar', 'rechazar', 'expulsar']:
            raise ValueError("Acción inválida. Debe ser: aprobar, rechazar o expulsar")

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # Validar permisos
        self.partido_service.validar_organizador(partido, organizador_id)

        # Obtener participación
        participacion = next(
            (
                p for p in db_instance.participaciones_db
                if p.id == participacion_id and p.partido_id == partido_id
            ),
            None,
        )
        if not participacion:
            raise ValueError("Participación no encontrada")

        # No puede gestionar su propia participación
        if participacion.jugador_id == organizador_id:
            raise ValueError("No puedes gestionar tu propia participación")

        # Ejecutar acción
        if accion == "aprobar":
            return self._aprobar(partido, participacion)
        elif accion == "rechazar":
            return self._rechazar(partido, participacion)
        elif accion == "expulsar":
            return self._expulsar(partido, participacion)

    def _aprobar(self, partido, participacion) -> dict:
        """Aprueba una participación pendiente"""
        if participacion.estado != EstadoParticipacion.PENDIENTE:
            raise ValueError("Solo se pueden aprobar participaciones pendientes")

        # Verificar cupo
        confirmados = len([
            p for p in db_instance.participaciones_db
            if p.partido_id == partido.id 
            and p.estado == EstadoParticipacion.CONFIRMADO
        ])
        if confirmados >= partido.capacidad_maxima:
            raise PartidoCompletoException("El partido está completo")

        # Aprobar
        participacion.estado = EstadoParticipacion.CONFIRMADO
        mensaje = f"{participacion.jugador_nombre} ha sido aprobado"

        return self._generar_respuesta(partido.id, mensaje)

    def _rechazar(self, partido, participacion) -> dict:
        """Rechaza una participación pendiente"""
        if participacion.estado != EstadoParticipacion.PENDIENTE:
            raise ValueError("Solo se pueden rechazar participaciones pendientes")

        # Rechazar
        participacion.estado = EstadoParticipacion.RECHAZADO
        mensaje = f"{participacion.jugador_nombre} ha sido rechazado"

        return self._generar_respuesta(partido.id, mensaje)

    def _expulsar(self, partido, participacion) -> dict:
        """Expulsa un participante confirmado"""
        if participacion.estado != EstadoParticipacion.CONFIRMADO:
            raise ValueError("Solo se pueden expulsar participaciones confirmadas")

        # Expulsar
        participacion.estado = EstadoParticipacion.CANCELADO
        mensaje = f"{participacion.jugador_nombre} ha sido expulsado del partido"

        return self._generar_respuesta(partido.id, mensaje)

    def _generar_respuesta(self, partido_id: int, mensaje: str) -> dict:
        """Genera la respuesta con conteos actualizados"""
        confirmados = len([
            p for p in db_instance.participaciones_db
            if p.partido_id == partido_id 
            and p.estado == EstadoParticipacion.CONFIRMADO
        ])
        pendientes = len([
            p for p in db_instance.participaciones_db
            if p.partido_id == partido_id 
            and p.estado == EstadoParticipacion.PENDIENTE
        ])
        
        partido = self.partido_repo.obtener_por_id(partido_id)

        return {
            "mensaje": mensaje,
            "partido_id": partido_id,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "capacidad_maxima": partido.capacidad_maxima,
        }