"""Caso de uso: Postularse a un Partido"""
from datetime import datetime
from app.domain.models.participacion import Participacion
from app.domain.enums.estado import TipoPartido, EstadoParticipacion
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PartidoCompletoException,
    ContrasenaIncorrectaException,
)
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class PostularsePartidoUseCase:
    """Caso de uso para postularse a un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.usuario_repo = UsuarioRepository(db_instance)

    def execute(
        self, 
        partido_id: int, 
        usuario_id: int, 
        contrasena: str = None
    ) -> dict:
        """Ejecuta el caso de uso"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # Validar que no sea el organizador
        if partido.organizador_id == usuario_id:
            raise ValueError("Ya eres el organizador de este partido")

        # Validar que no esté ya postulado
        ya_postulado = any(
            p.partido_id == partido_id 
            and p.jugador_id == usuario_id 
            and p.estado in [EstadoParticipacion.CONFIRMADO, EstadoParticipacion.PENDIENTE]
            for p in db_instance.participaciones_db
        )
        if ya_postulado:
            raise ValueError("Ya tienes una postulación activa en este partido")

        # Validar contraseña si es privado
        if partido.tipo_partido == TipoPartido.PRIVADO:
            if not contrasena:
                raise ValueError("Este partido requiere contraseña")
            if contrasena != partido.contrasena:
                raise ContrasenaIncorrectaException("Contraseña incorrecta")

        # Validar cupo
        confirmados = len([
            p for p in db_instance.participaciones_db
            if p.partido_id == partido_id 
            and p.estado == EstadoParticipacion.CONFIRMADO
        ])
        if confirmados >= partido.capacidad_maxima:
            raise PartidoCompletoException("El partido está completo")

        # Crear participación
        nueva_participacion_id = max(
            [p.id for p in db_instance.participaciones_db], 
            default=0
        ) + 1

        nueva_participacion = Participacion(
            id=nueva_participacion_id,
            partido_id=partido_id,
            jugador_id=usuario_id,
            jugador_nombre=usuario.nombre,
            estado=EstadoParticipacion.PENDIENTE,
            fecha_postulacion=datetime.now(),
        )
        db_instance.participaciones_db.append(nueva_participacion)

        # Contar pendientes
        pendientes = len([
            p for p in db_instance.participaciones_db
            if p.partido_id == partido_id 
            and p.estado == EstadoParticipacion.PENDIENTE
        ])

        return {
            "mensaje": "Postulación enviada. Esperando aprobación del organizador",
            "partido_id": partido_id,
            "estado": "PENDIENTE",
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "capacidad_maxima": partido.capacidad_maxima,
        }