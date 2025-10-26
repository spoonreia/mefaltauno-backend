"""Caso de uso: Gestionar Participación (aprobar/rechazar/expulsar)"""
from app.domain.enums.estado import EstadoParticipacion
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PartidoCompletoException,
)
from app.domain.services.partido_service import PartidoService
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class GestionarParticipacionUseCase:
    """Caso de uso para gestionar participaciones"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)
        self.partido_service = PartidoService()

    def execute(
        self,
        partido_id: int,
        participacion_id: int,
        organizador_id: int,
        accion: str,
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
        participacion = self.participacion_repo.obtener_por_id(participacion_id)
        if not participacion or participacion.partido_id != partido_id:
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

        return None

    def _aprobar(self, partido, participacion) -> dict:
        """Aprueba una participación pendiente"""
        if participacion.estado != EstadoParticipacion.PENDIENTE:
            raise ValueError("Solo se pueden aprobar participaciones pendientes")

        # Verificar cupo
        confirmados = self.participacion_repo.contar_por_estado(
            partido.id, EstadoParticipacion.CONFIRMADO
        )
        if confirmados >= partido.capacidad_maxima:
            raise PartidoCompletoException("El partido está completo")

        # Aprobar
        participacion.estado = EstadoParticipacion.CONFIRMADO
        self.participacion_repo.actualizar(participacion)
        mensaje = f"{participacion.jugador_nombre} ha sido aprobado"

        return self._generar_respuesta(partido.id, mensaje)

    def _rechazar(self, partido, participacion) -> dict:
        """Rechaza una participación pendiente"""
        if participacion.estado != EstadoParticipacion.PENDIENTE:
            raise ValueError("Solo se pueden rechazar participaciones pendientes")

        # Rechazar
        participacion.estado = EstadoParticipacion.RECHAZADO
        self.participacion_repo.actualizar(participacion)
        mensaje = f"{participacion.jugador_nombre} ha sido rechazado"

        return self._generar_respuesta(partido.id, mensaje)

    def _expulsar(self, partido, participacion) -> dict:
        """Expulsa un participante confirmado"""
        if participacion.estado != EstadoParticipacion.CONFIRMADO:
            raise ValueError("Solo se pueden expulsar participaciones confirmadas")

        # Expulsar
        participacion.estado = EstadoParticipacion.CANCELADO
        self.participacion_repo.actualizar(participacion)
        mensaje = f"{participacion.jugador_nombre} ha sido expulsado del partido"

        return self._generar_respuesta(partido.id, mensaje)

    def _generar_respuesta(self, partido_id: int, mensaje: str) -> dict:
        """Genera la respuesta con conteos actualizados"""
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO
        )
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE
        )
        
        partido = self.partido_repo.obtener_por_id(partido_id)

        return {
            "mensaje": mensaje,
            "partido_id": partido_id,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "capacidad_maxima": partido.capacidad_maxima,
        }