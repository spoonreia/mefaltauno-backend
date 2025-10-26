"""Caso de uso: Invitar Jugador a Partido"""
from datetime import datetime
from app.domain.models.invitacion import Invitacion
from app.domain.enums.estado import EstadoInvitacion
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
)
from app.domain.services.partido_service import PartidoService
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.repositories.invitacion_repository import InvitacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class InvitarJugadorUseCase:
    """Caso de uso para invitar un jugador a un partido"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.usuario_repo = UsuarioRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)
        self.invitacion_repo = InvitacionRepository(database_client)
        self.partido_service = PartidoService()

    def execute(
        self,
        partido_id: int,
        jugador_id: int,
        organizador_id: int,
    ) -> dict:
        """Ejecuta el caso de uso"""

        # Verificar organizador
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise ValueError("Organizador no encontrado")

        # Verificar jugador
        jugador = self.usuario_repo.obtener_por_id(jugador_id)
        if not jugador:
            raise ValueError("Jugador no encontrado")

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # Validar permisos
        self.partido_service.validar_organizador(partido, organizador_id)

        # No puede invitarse a sí mismo
        if jugador_id == organizador_id:
            raise ValueError("No puedes invitarte a ti mismo")

        # Verificar que no esté ya participando
        ya_participa = self.participacion_repo.existe_participacion_activa(partido_id, jugador_id)
        if ya_participa:
            raise ValueError("El jugador ya está participando en este partido")

        # Verificar que no tenga invitación pendiente
        ya_invitado = self.invitacion_repo.existe_invitacion_pendiente(partido_id, jugador_id)
        if ya_invitado:
            raise ValueError("El jugador ya tiene una invitación pendiente")

        # Crear invitación
        # Los datos del partido (titulo, fecha_hora, ubicacion) se obtendrán por JOIN al leerlo
        nueva_invitacion = Invitacion(
            id=0,
            partido_id=partido_id,
            partido_titulo=partido.titulo,  # Solo para el objeto, no se guarda en DB
            partido_fecha_hora=partido.fecha_hora,  # Solo para el objeto, no se guarda en DB
            partido_ubicacion=partido.ubicacion_texto,  # Solo para el objeto, no se guarda en DB
            jugador_id=jugador_id,
            estado=EstadoInvitacion.PENDIENTE,
            fecha_invitacion=datetime.now(),
        )
        invitacion_creada = self.invitacion_repo.crear(nueva_invitacion)

        return {
            "mensaje": f"Invitación enviada a {jugador.nombre}",
            "invitacion_id": invitacion_creada.id,
        }