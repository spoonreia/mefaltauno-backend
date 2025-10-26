"""Caso de uso: Responder Invitación"""
from datetime import datetime
from app.domain.models.participacion import Participacion
from app.domain.enums.estado import EstadoInvitacion, EstadoParticipacion
from app.domain.exceptions.partido_exceptions import PartidoCompletoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.repositories.invitacion_repository import InvitacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class ResponderInvitacionUseCase:
    """Caso de uso para responder una invitación"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.usuario_repo = UsuarioRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)
        self.invitacion_repo = InvitacionRepository(database_client)

    def execute(self, invitacion_id: int, usuario_id: int, aceptar: bool) -> dict:
        """Ejecuta el caso de uso"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Buscar invitación
        invitacion = self.invitacion_repo.obtener_por_id(invitacion_id)
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
            confirmados = self.participacion_repo.contar_por_estado(
                invitacion.partido_id, EstadoParticipacion.CONFIRMADO
            )
            if confirmados >= partido.capacidad_maxima:
                raise PartidoCompletoException("El partido está completo")

            # ✅ VERIFICAR SI YA EXISTE UNA PARTICIPACIÓN
            participacion_existente = self.participacion_repo.obtener_por_partido_y_jugador(
                invitacion.partido_id, usuario_id
            )

            if participacion_existente:
                # Si ya existe, actualizar su estado a CONFIRMADO
                participacion_existente.estado = EstadoParticipacion.CONFIRMADO
                self.participacion_repo.actualizar(participacion_existente)
            else:
                # Si no existe, crear nueva participación confirmada
                nueva_participacion = Participacion(
                    id=0,
                    partido_id=invitacion.partido_id,
                    jugador_id=usuario_id,
                    jugador_nombre=usuario.nombre,  # Solo para el objeto, no se guarda en DB
                    estado=EstadoParticipacion.CONFIRMADO,
                    fecha_postulacion=datetime.now(),
                )
                self.participacion_repo.crear(nueva_participacion)

            # Marcar invitación como aceptada
            invitacion.estado = EstadoInvitacion.ACEPTADA
            self.invitacion_repo.actualizar(invitacion)
            mensaje = "Invitación aceptada. Te has unido al partido"
        else:
            # Marcar invitación como rechazada
            invitacion.estado = EstadoInvitacion.RECHAZADA
            self.invitacion_repo.actualizar(invitacion)
            mensaje = "Invitación rechazada"

        return {
            "mensaje": mensaje,
            "partido_id": invitacion.partido_id,
        }