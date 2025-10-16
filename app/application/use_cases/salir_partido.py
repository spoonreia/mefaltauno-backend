"""Caso de uso: Salir de un Partido"""
from app.domain.enums.estado import EstadoParticipacion
from app.domain.exceptions.partido_exceptions import PartidoNoEncontradoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class SalirPartidoUseCase:
    """Caso de uso para salir de un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.usuario_repo = UsuarioRepository(db_instance)

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
        participacion = next(
            (
                p for p in db_instance.participaciones_db
                if p.partido_id == partido_id
                and p.jugador_id == usuario_id
                and p.estado in [EstadoParticipacion.PENDIENTE, EstadoParticipacion.CONFIRMADO]
            ),
            None,
        )
        if not participacion:
            raise ValueError("No tienes una participación activa en este partido")

        # Guardar estado anterior
        estado_anterior = participacion.estado

        # Cancelar participación
        participacion.estado = EstadoParticipacion.CANCELADO

        # Contar participantes
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

        return {
            "mensaje": f"Has salido del partido (estabas {estado_anterior})",
            "partido_id": partido_id,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
        }