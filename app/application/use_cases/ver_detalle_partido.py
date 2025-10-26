"""Caso de uso: Ver Detalle de Partido"""
from app.domain.enums.estado import EstadoParticipacion
from app.domain.exceptions.partido_exceptions import PartidoNoEncontradoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class VerDetallePartidoUseCase:
    """Caso de uso para ver el detalle completo de un partido"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.usuario_repo = UsuarioRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)

    def execute(self, partido_id: int, usuario_id: int) -> dict:
        """Ejecuta el caso de uso"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # Obtener participantes (confirmados y pendientes) - YA INCLUYE jugador_nombre por el JOIN
        participaciones = self.participacion_repo.obtener_por_partido(partido_id)

        participantes = []
        for p in participaciones:
            # Solo incluir confirmados y pendientes
            if p.estado in [EstadoParticipacion.CONFIRMADO, EstadoParticipacion.PENDIENTE]:
                participantes.append({
                    "id": p.id,
                    "partido_id": p.partido_id,
                    "jugador_id": p.jugador_id,
                    "jugador_nombre": p.jugador_nombre,
                    "estado": p.estado,
                    "fecha_postulacion": p.fecha_postulacion,
                })

        # Ordenar: confirmados primero, luego por fecha
        participantes.sort(
            key=lambda x: (
                x["estado"] != EstadoParticipacion.CONFIRMADO,
                x["fecha_postulacion"],
            )
        )

        # Contar participantes
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO
        )
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE
        )

        # Tiene cupo?
        tiene_cupo = confirmados < partido.capacidad_maxima

        # Obtener organizador
        organizador = self.usuario_repo.obtener_por_id(partido.organizador_id)

        # Construir respuesta
        detalle = {
            "id": partido.id,
            "titulo": partido.titulo,
            "dinero_por_persona": partido.dinero_por_persona,
            "descripcion": partido.descripcion,
            "fecha_hora": partido.fecha_hora,
            "latitud": partido.latitud,
            "longitud": partido.longitud,
            "ubicacion_texto": partido.ubicacion_texto,
            "capacidad_maxima": partido.capacidad_maxima,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "organizador_id": partido.organizador_id,
            "organizador_nombre": organizador.nombre if organizador else "Desconocido",
            "tipo_partido": partido.tipo_partido,
            "tipo_futbol": partido.tipo_futbol,
            "edad_minima": partido.edad_minima,
            "estado": partido.estado,
            "tiene_cupo": tiene_cupo,
            "participantes": participantes,
        }

        return detalle