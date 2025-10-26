"""Caso de uso: Obtener Calendario de Partidos"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.domain.enums.estado import EstadoParticipacion
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.database.database_service import DatabaseConnection
from sqlalchemy import text


class ObtenerCalendarioUseCase:
    """Caso de uso para obtener el calendario de partidos de un usuario"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.usuario_repo = UsuarioRepository(database_client)

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

        # Query SQL para obtener partidos del usuario
        sql = text(
            """
                SELECT 
                    p.id,
                    p.titulo,
                    p.fecha_hora,
                    p.ubicacion_texto,
                    p.organizador_id,
                    p.capacidad_maxima,
                    p.tipo_partido,
                    (p.organizador_id = :usuario_id) as es_organizador,
                    (SELECT COUNT(*) 
                     FROM participaciones part 
                     WHERE part.partido_id = p.id 
                     AND part.estado = :estado_confirmado) as jugadores_confirmados
                FROM partidos p
                INNER JOIN participaciones pa ON p.id = pa.partido_id
                WHERE pa.jugador_id = :usuario_id
                AND pa.estado = :estado_confirmado
                AND p.fecha_hora >= :fecha_desde
                AND p.fecha_hora <= :fecha_hasta
                AND p.fecha_hora >= :ahora
                ORDER BY p.fecha_hora ASC
            """
        )

        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, {
                "usuario_id": usuario_id,
                "estado_confirmado": EstadoParticipacion.CONFIRMADO.value,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "ahora": ahora
            }).fetchall()

        # Convertir resultados a lista de diccionarios
        partidos_usuario = []
        for row in results:
            partido_calendario = {
                "id": row.id,
                "titulo": row.titulo,
                "fecha_hora": row.fecha_hora,
                "ubicacion_texto": row.ubicacion_texto,
                "es_organizador": bool(row.es_organizador),
                "jugadores_confirmados": row.jugadores_confirmados,
                "capacidad_maxima": row.capacidad_maxima,
                "tipo_partido": row.tipo_partido,
            }
            partidos_usuario.append(partido_calendario)

        return partidos_usuario