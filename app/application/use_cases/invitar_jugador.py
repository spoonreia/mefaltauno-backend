"""Caso de uso: Invitar Jugador a Partido"""
from datetime import datetime
from app.domain.models.invitacion import Invitacion
from app.domain.enums.estado import EstadoParticipacion, EstadoInvitacion
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PermisosDenegadosException,
)
from app.domain.services.partido_service import PartidoService
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class InvitarJugadorUseCase:
    """Caso de uso para invitar un jugador a un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.usuario_repo = UsuarioRepository(db_instance)
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
        ya_participa = any(
            p.partido_id == partido_id
            and p.jugador_id == jugador_id
            and p.estado in [EstadoParticipacion.CONFIRMADO, EstadoParticipacion.PENDIENTE]
            for p in db_instance.participaciones_db
        )
        if ya_participa:
            raise ValueError("El jugador ya está participando en este partido")

        # Verificar que no tenga invitación pendiente
        ya_invitado = any(
            i.partido_id == partido_id
            and i.jugador_id == jugador_id
            and i.estado == EstadoInvitacion.PENDIENTE
            for i in db_instance.invitaciones_db
        )
        if ya_invitado:
            raise ValueError("El jugador ya tiene una invitación pendiente")

        # Crear invitación
        nueva_invitacion_id = max(
            [i.id for i in db_instance.invitaciones_db],
            default=0
        ) + 1

        nueva_invitacion = Invitacion(
            id=nueva_invitacion_id,
            partido_id=partido_id,
            partido_titulo=partido.titulo,
            partido_fecha_hora=partido.fecha_hora,
            partido_ubicacion=partido.ubicacion_texto,
            jugador_id=jugador_id,
            estado=EstadoInvitacion.PENDIENTE,
            fecha_invitacion=datetime.now(),
        )
        db_instance.invitaciones_db.append(nueva_invitacion)

        return {
            "mensaje": f"Invitación enviada a {jugador.nombre}",
            "invitacion_id": nueva_invitacion_id,
        }