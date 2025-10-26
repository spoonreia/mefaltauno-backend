"""Caso de uso: Buscar Partidos"""
from typing import List, Optional
from datetime import datetime
from app.domain.enums.estado import TipoFutbol, EstadoParticipacion
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.database.database_service import DatabaseConnection
from app.infrastructure.utils.calculadora_distancia import calcular_distancia
from sqlalchemy import text


class BuscarPartidosUseCase:
    """Caso de uso para buscar partidos"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.usuario_repo = UsuarioRepository(database_client)

    def execute(
        self,
        usuario_id: int,
        titulo: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        distancia_maxima_km: float = 5.0,
        tipo_futbol: Optional[TipoFutbol] = None,
        edad_minima: Optional[int] = None,
    ) -> List[dict]:
        """Ejecuta el caso de uso"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Construir query SQL
        sql_parts = [
            """
            SELECT DISTINCT
                p.id,
                p.titulo,
                p.dinero_por_persona,
                p.descripcion,
                p.fecha_hora,
                p.latitud,
                p.longitud,
                p.ubicacion_texto,
                p.capacidad_maxima,
                p.organizador_id,
                p.tipo_partido,
                p.tipo_futbol,
                p.edad_minima,
                p.estado,
                (SELECT COUNT(*) 
                 FROM participaciones part 
                 WHERE part.partido_id = p.id 
                 AND part.estado = :estado_confirmado) as jugadores_confirmados,
                (SELECT u.nombre FROM usuarios u WHERE u.id = p.organizador_id) as organizador_nombre
            FROM partidos p
            WHERE p.id NOT IN (
                SELECT pa.partido_id 
                FROM participaciones pa 
                WHERE pa.jugador_id = :usuario_id 
                AND pa.estado IN (:estado_confirmado, :estado_pendiente)
            )
            AND p.fecha_hora >= NOW()
            """
        ]

        params = {
            "usuario_id": usuario_id,
            "estado_confirmado": EstadoParticipacion.CONFIRMADO.value,
            "estado_pendiente": EstadoParticipacion.PENDIENTE.value
        }

        # Filtros opcionales
        if titulo:
            sql_parts.append("AND LOWER(p.titulo) LIKE :titulo")
            params["titulo"] = f"%{titulo.lower()}%"

        if fecha_desde:
            sql_parts.append("AND p.fecha_hora >= :fecha_desde")
            params["fecha_desde"] = fecha_desde

        if fecha_hasta:
            sql_parts.append("AND p.fecha_hora <= :fecha_hasta")
            params["fecha_hasta"] = fecha_hasta

        if tipo_futbol:
            sql_parts.append("AND p.tipo_futbol = :tipo_futbol")
            params["tipo_futbol"] = tipo_futbol.value

        if edad_minima is not None:
            sql_parts.append("AND p.edad_minima <= :edad_minima")
            params["edad_minima"] = edad_minima

        sql = text(" ".join(sql_parts))

        # Ejecutar query
        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, params).fetchall()

        # Filtrar por distancia y capacidad
        resultados = []
        for row in results:
            # Solo partidos con cupo
            if row.jugadores_confirmados >= row.capacidad_maxima:
                continue

            # Calcular distancia
            distancia = calcular_distancia(
                float(usuario.latitud),
                float(usuario.longitud),
                float(row.latitud),
                float(row.longitud),
            )

            # Filtrar por distancia
            if distancia > distancia_maxima_km:
                continue

            # Crear resultado
            resultado = {
                "id": row.id,
                "titulo": row.titulo,
                "dinero_por_persona": row.dinero_por_persona,
                "descripcion": row.descripcion,
                "fecha_hora": row.fecha_hora,
                "latitud": row.latitud,
                "longitud": row.longitud,
                "ubicacion_texto": row.ubicacion_texto,
                "capacidad_maxima": row.capacidad_maxima,
                "jugadores_confirmados": row.jugadores_confirmados,
                "organizador_id": row.organizador_id,
                "organizador_nombre": row.organizador_nombre,
                "tipo_partido": row.tipo_partido,
                "tipo_futbol": row.tipo_futbol,
                "edad_minima": row.edad_minima,
                "estado": row.estado,
                "tiene_cupo": True,
                "distancia_km": round(distancia, 2),
            }
            resultados.append(resultado)

        # Ordenar por distancia
        resultados.sort(key=lambda x: x["distancia_km"])

        return resultados