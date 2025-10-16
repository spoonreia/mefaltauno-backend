"""Caso de uso: Ver Detalle de Partido"""
from typing import List
from app.domain.enums.estado import EstadoParticipacion
from app.domain.exceptions.partido_exceptions import PartidoNoEncontradoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class VerDetallePartidoUseCase:
    """Caso de uso para ver el detalle completo de un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.usuario_repo = UsuarioRepository(db_instance)

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

        # Obtener participantes (confirmados y pendientes)
        participantes = [
            {
                "id": p.id,
                "partido_id": p.partido_id,
                "jugador_id": p.jugador_id,
                "jugador_nombre": p.jugador_nombre,
                "estado": p.estado,
                "fecha_postulacion": p.fecha_postulacion,
            }
            for p in db_instance.participaciones_db
            if p.partido_id == partido_id
            and p.estado in [EstadoParticipacion.CONFIRMADO, EstadoParticipacion.PENDIENTE]
        ]

        # Ordenar: confirmados primero, luego por fecha
        participantes.sort(
            key=lambda x: (
                x["estado"] != EstadoParticipacion.CONFIRMADO,
                x["fecha_postulacion"],
            )
        )

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