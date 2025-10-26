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
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class PostularsePartidoUseCase:
    """Caso de uso para postularse a un partido"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.usuario_repo = UsuarioRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)

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
        ya_postulado = self.participacion_repo.existe_participacion_activa(partido_id, usuario_id)
        if ya_postulado:
            raise ValueError("Ya tienes una postulación activa en este partido")

        # Validar contraseña si es privado
        if partido.tipo_partido == TipoPartido.PRIVADO:
            if not contrasena:
                raise ValueError("Este partido requiere contraseña")
            if contrasena != partido.contrasena:
                raise ContrasenaIncorrectaException("Contraseña incorrecta")

        # Validar cupo
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO
        )
        if confirmados >= partido.capacidad_maxima:
            raise PartidoCompletoException("El partido está completo")

        # Crear participación (el nombre del jugador se obtendrá por JOIN al leerlo)
        nueva_participacion = Participacion(
            id=0,
            partido_id=partido_id,
            jugador_id=usuario_id,
            jugador_nombre=usuario.nombre,  # Solo para el objeto, no se guarda en DB
            estado=EstadoParticipacion.PENDIENTE,
            fecha_postulacion=datetime.now(),
        )
        self.participacion_repo.crear(nueva_participacion)

        # Contar pendientes
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE
        )

        return {
            "mensaje": "Postulación enviada. Esperando aprobación del organizador",
            "partido_id": partido_id,
            "estado": "PENDIENTE",
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "capacidad_maxima": partido.capacidad_maxima,
        }