"""Caso de uso: Responder Invitación"""
from datetime import datetime
from app.domain.models.participacion import Participacion
from app.domain.enums.estado import EstadoInvitacion, EstadoParticipacion
from app.domain.exceptions.partido_exceptions import PartidoCompletoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class ResponderInvitacionUseCase:
    """Caso de uso para responder una invitación"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.usuario_repo = UsuarioRepository(db_instance)

    def execute(self, invitacion_id: int, usuario_id: int, aceptar: bool) -> dict:
        """Ejecuta el caso de uso"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Buscar invitación
        invitacion = next(
            (i for i in db_instance.invitaciones_db if i.id == invitacion_id),
            None,
        )
        if not invitacion:
            raise ValueError("Invitación no encontrada")

        # Verificar que sea para este usuario
        if invitacion.jugador_id != usuario_id:
            raise ValueError("No puedes responder esta invitación")

        # Verificar que esté pendiente
        if invitacion.estado != EstadoInvitacion.PENDIENTE:
            raise ValueError("Esta invitación ya fue respondida")

        if aceptar:
            # Obtener partido
            partido = self.partido_repo.obtener_por_id(invitacion.partido_id)
            if not partido:
                raise ValueError("Partido no encontrado")

            # Verificar cupo
            confirmados = len([
                p for p in db_instance.participaciones_db
                if p.partido_id == invitacion.partido_id
                and p.estado == EstadoParticipacion.CONFIRMADO
            ])
            if confirmados >= partido.capacidad_maxima:
                raise PartidoCompletoException("El partido está completo")

            # Crear participación confirmada
            nueva_participacion_id = max(
                [p.id for p in db_instance.participaciones_db],
                default=0
            ) + 1

            nueva_participacion = Participacion(
                id=nueva_participacion_id,
                partido_id=invitacion.partido_id,
                jugador_id=usuario_id,
                jugador_nombre=usuario.nombre,
                estado=EstadoParticipacion.CONFIRMADO,
                fecha_postulacion=datetime.now(),
            )
            db_instance.participaciones_db.append(nueva_participacion)

            # Marcar invitación como aceptada
            invitacion.estado = EstadoInvitacion.ACEPTADA
            mensaje = "Invitación aceptada. Te has unido al partido"
        else:
            # Marcar invitación como rechazada
            invitacion.estado = EstadoInvitacion.RECHAZADA
            mensaje = "Invitación rechazada"

        return {
            "mensaje": mensaje,
            "partido_id": invitacion.partido_id,
        }