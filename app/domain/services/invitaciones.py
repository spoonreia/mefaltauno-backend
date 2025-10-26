"""Servicio de dominio para Invitaciones"""
from typing import List, Dict, Any
from datetime import datetime

from app.domain.repositories.invitaciones import InvitacionRepositoryInterface
from app.domain.repositories.usuarios import UsuarioRepositoryInterface
from app.domain.repositories.partidos import PartidoRepositoryInterface
from app.domain.repositories.participaciones import ParticipacionRepositoryInterface
from app.domain.exceptions import (
    UsuarioNoEncontradoException,
    InvitacionNoEncontradaException,
    PartidoCompletoException,
)
from app.domain.schemas.invitaciones import EstadoInvitacion
from app.domain.schemas.partidos import EstadoParticipacion
from app.domain import error_messages as msg


class InvitacionService:
    """Servicio de dominio para gestionar invitaciones"""

    def __init__(
            self,
            invitacion_repo: InvitacionRepositoryInterface,
            usuario_repo: UsuarioRepositoryInterface,
            partido_repo: PartidoRepositoryInterface,
            participacion_repo: ParticipacionRepositoryInterface,
    ):
        self.invitacion_repo = invitacion_repo
        self.usuario_repo = usuario_repo
        self.partido_repo = partido_repo
        self.participacion_repo = participacion_repo

    # ============================================
    # OBTENER INVITACIONES
    # ============================================

    def obtener_por_usuario(
            self,
            usuario_id: int,
            estado: EstadoInvitacion = EstadoInvitacion.PENDIENTE
    ) -> List[Dict[str, Any]]:
        """Obtiene las invitaciones de un usuario"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Obtener invitaciones
        return self.invitacion_repo.obtener_por_jugador(usuario_id, estado.value)

    # ============================================
    # RESPONDER INVITACIÓN
    # ============================================

    def responder(
            self,
            invitacion_id: int,
            usuario_id: int,
            aceptar: bool
    ) -> Dict[str, Any]:
        """Responde a una invitación (aceptar o rechazar)"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Buscar invitación
        invitacion = self.invitacion_repo.obtener_por_id(invitacion_id)
        if not invitacion:
            raise InvitacionNoEncontradaException(msg.INVITACION_NO_ENCONTRADA)

        # Verificar que sea para este usuario
        if invitacion['jugador_id'] != usuario_id:
            raise ValueError(msg.INVITACION_NO_AUTORIZADA)

        # Verificar que esté pendiente
        if invitacion['estado'] != EstadoInvitacion.PENDIENTE.value:
            raise ValueError(msg.INVITACION_YA_RESPONDIDA)

        if aceptar:
            # Obtener partido
            partido = self.partido_repo.obtener_por_id(invitacion['partido_id'])
            if not partido:
                raise ValueError(msg.PARTIDO_NO_ENCONTRADO)

            # Verificar cupo
            confirmados = self.participacion_repo.contar_por_estado(
                invitacion['partido_id'], EstadoParticipacion.CONFIRMADO.value
            )
            if confirmados >= partido['capacidad_maxima']:
                raise PartidoCompletoException(msg.PARTIDO_COMPLETO)

            # Verificar si ya existe una participación
            participacion_existente = self.participacion_repo.obtener_por_partido_y_jugador(
                invitacion['partido_id'], usuario_id
            )

            if participacion_existente:
                # Si ya existe, actualizar su estado a CONFIRMADO
                participacion_existente['estado'] = EstadoParticipacion.CONFIRMADO.value
                self.participacion_repo.actualizar(
                    participacion_existente['id'],
                    participacion_existente
                )
            else:
                # Si no existe, crear nueva participación confirmada
                participacion_data = {
                    'partido_id': invitacion['partido_id'],
                    'jugador_id': usuario_id,
                    'estado': EstadoParticipacion.CONFIRMADO.value,
                    'fecha_postulacion': datetime.now(),
                }
                self.participacion_repo.crear(participacion_data)

            # Marcar invitación como aceptada
            invitacion['estado'] = EstadoInvitacion.ACEPTADA.value
            self.invitacion_repo.actualizar(invitacion_id, invitacion)

            mensaje = msg.INVITACION_ACEPTADA
        else:
            # Marcar invitación como rechazada
            invitacion['estado'] = EstadoInvitacion.RECHAZADA.value
            self.invitacion_repo.actualizar(invitacion_id, invitacion)

            mensaje = msg.INVITACION_RECHAZADA

        return {
            "mensaje": mensaje,
            "partido_id": invitacion['partido_id'],
        }