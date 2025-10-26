"""Caso de uso: Salir de un Partido"""
from app.domain.enums.estado import EstadoParticipacion
from app.domain.exceptions.partido_exceptions import PartidoNoEncontradoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class SalirPartidoUseCase:
    """Caso de uso para salir de un partido"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.usuario_repo = UsuarioRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)

    def execute(self, partido_id: int, usuario_id: int) -> dict:
        """Ejecuta el caso de uso"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # El organizador no puede salir
        if partido.organizador_id == usuario_id:
            raise ValueError("El organizador no puede salir de su propio partido")

        # Buscar participación activa
        participacion = self.participacion_repo.obtener_por_partido_y_jugador(partido_id, usuario_id)

        if not participacion or participacion.estado not in [
            EstadoParticipacion.PENDIENTE,
            EstadoParticipacion.CONFIRMADO
        ]:
            raise ValueError("No tienes una participación activa en este partido")

        # Guardar estado anterior
        estado_anterior = participacion.estado

        # Cancelar participación
        participacion.estado = EstadoParticipacion.CANCELADO
        self.participacion_repo.actualizar(participacion)

        # Contar participantes
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO
        )
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE
        )

        return {
            "mensaje": f"Has salido del partido (estabas {estado_anterior.value})",
            "partido_id": partido_id,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
        }