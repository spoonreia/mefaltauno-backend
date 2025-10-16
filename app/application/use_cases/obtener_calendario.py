"""Caso de uso: Obtener Calendario de Partidos"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.domain.enums.estado import EstadoParticipacion
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class ObtenerCalendarioUseCase:
    """Caso de uso para obtener el calendario de partidos de un usuario"""

    def __init__(self):
        self.usuario_repo = UsuarioRepository(db_instance)

    def execute(
        self,
        usuario_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> List[dict]:
        """Ejecuta el caso de uso"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Fechas por defecto
        ahora = datetime.now()
        if not fecha_desde:
            fecha_desde = ahora
        else:
            if fecha_desde.tzinfo is not None:
                fecha_desde = fecha_desde.replace(tzinfo=None)

        if not fecha_hasta:
            fecha_hasta = ahora + timedelta(days=30)
        else:
            if fecha_hasta.tzinfo is not None:
                fecha_hasta = fecha_hasta.replace(tzinfo=None)

        # Buscar partidos del usuario
        partidos_usuario = []

        for participacion in db_instance.participaciones_db:
            # Solo participaciones del usuario
            if participacion.jugador_id != usuario_id:
                continue

            # Solo confirmados
            if participacion.estado != EstadoParticipacion.CONFIRMADO:
                continue

            # Buscar partido
            partido = next(
                (p for p in db_instance.partidos_db if p["id"] == participacion.partido_id),
                None,
            )
            if not partido:
                continue

            # Filtrar por fecha
            if partido["fecha_hora"] < fecha_desde or partido["fecha_hora"] > fecha_hasta:
                continue

            # No incluir partidos pasados
            if partido["fecha_hora"] < ahora:
                continue

            # Contar confirmados
            confirmados = len([
                p for p in db_instance.participaciones_db
                if p.partido_id == partido["id"] 
                and p.estado == EstadoParticipacion.CONFIRMADO
            ])

            # Es organizador?
            es_organizador = partido["organizador_id"] == usuario_id

            # Crear item de calendario
            partido_calendario = {
                "id": partido["id"],
                "titulo": partido["titulo"],
                "fecha_hora": partido["fecha_hora"],
                "ubicacion_texto": partido["ubicacion_texto"],
                "es_organizador": es_organizador,
                "jugadores_confirmados": confirmados,
                "capacidad_maxima": partido["capacidad_maxima"],
                "tipo_partido": partido["tipo_partido"],  # Agregado para mostrar candado
            }
            partidos_usuario.append(partido_calendario)

        # Ordenar por fecha
        partidos_usuario.sort(key=lambda x: x["fecha_hora"])

        return partidos_usuario