"""Repositorio de Partidos"""
from typing import List, Optional
from datetime import datetime
from app.domain.models.partido import Partido
from app.domain.enums.estado import TipoFutbol, TipoPartido, EstadoPartido
from app.infrastructure.database.database_service import DatabaseConnection
from sqlalchemy import text


class PartidoRepository:
    """Repositorio de partidos conectado a la base de datos"""

    def __init__(self, database_client: DatabaseConnection):
        super().__init__()
        self.database_client = database_client

    def crear(self, partido: Partido) -> Partido:
        """Crea un nuevo partido"""
        sql = text(
            """
            INSERT INTO partidos (
                titulo, dinero_por_persona, descripcion, fecha_hora,
                latitud, longitud, ubicacion_texto, capacidad_maxima,
                organizador_id, tipo_partido, tipo_futbol, edad_minima,
                estado, contrasena
            ) VALUES (
                :titulo, :dinero_por_persona, :descripcion, :fecha_hora,
                :latitud, :longitud, :ubicacion_texto, :capacidad_maxima,
                :organizador_id, :tipo_partido, :tipo_futbol, :edad_minima,
                :estado, :contrasena
            )
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "titulo": partido.titulo,
                "dinero_por_persona": partido.dinero_por_persona,
                "descripcion": partido.descripcion,
                "fecha_hora": partido.fecha_hora,
                "latitud": partido.latitud,
                "longitud": partido.longitud,
                "ubicacion_texto": partido.ubicacion_texto,
                "capacidad_maxima": partido.capacidad_maxima,
                "organizador_id": partido.organizador_id,
                "tipo_partido": partido.tipo_partido.value,
                "tipo_futbol": partido.tipo_futbol.value,
                "edad_minima": partido.edad_minima,
                "estado": partido.estado.value,
                "contrasena": partido.contrasena
            })
            db.commit()
            partido.id = result.lastrowid

        return partido

    def obtener_por_id(self, partido_id: int) -> Optional[Partido]:
        """Obtiene un partido por ID"""
        sql = text(
            """
            SELECT 
                id, titulo, dinero_por_persona, descripcion, fecha_hora,
                latitud, longitud, ubicacion_texto, capacidad_maxima,
                organizador_id, tipo_partido, tipo_futbol, edad_minima,
                estado, contrasena
            FROM partidos
            WHERE id = :partido_id
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"partido_id": partido_id}).fetchone()
            if result is None:
                return None

        return Partido(
            id=result.id,
            titulo=result.titulo,
            dinero_por_persona=result.dinero_por_persona,
            descripcion=result.descripcion,
            fecha_hora=result.fecha_hora,
            latitud=result.latitud,
            longitud=result.longitud,
            ubicacion_texto=result.ubicacion_texto,
            capacidad_maxima=result.capacidad_maxima,
            organizador_id=result.organizador_id,
            tipo_partido=TipoPartido(result.tipo_partido),
            tipo_futbol=TipoFutbol(result.tipo_futbol),
            edad_minima=result.edad_minima,
            estado=EstadoPartido(result.estado),
            contrasena=result.contrasena
        )

    def actualizar(self, partido: Partido) -> Partido:
        """Actualiza un partido existente"""
        sql = text(
            """
            UPDATE partidos 
            SET 
                titulo = :titulo,
                dinero_por_persona = :dinero_por_persona,
                descripcion = :descripcion,
                fecha_hora = :fecha_hora,
                latitud = :latitud,
                longitud = :longitud,
                ubicacion_texto = :ubicacion_texto,
                capacidad_maxima = :capacidad_maxima,
                tipo_partido = :tipo_partido,
                tipo_futbol = :tipo_futbol,
                edad_minima = :edad_minima,
                estado = :estado,
                contrasena = :contrasena
            WHERE id = :id
            """
        )

        with self.database_client.get_session("tt") as db:
            db.execute(sql, {
                "id": partido.id,
                "titulo": partido.titulo,
                "dinero_por_persona": partido.dinero_por_persona,
                "descripcion": partido.descripcion,
                "fecha_hora": partido.fecha_hora,
                "latitud": partido.latitud,
                "longitud": partido.longitud,
                "ubicacion_texto": partido.ubicacion_texto,
                "capacidad_maxima": partido.capacidad_maxima,
                "tipo_partido": partido.tipo_partido.value,
                "tipo_futbol": partido.tipo_futbol.value,
                "edad_minima": partido.edad_minima,
                "estado": partido.estado.value,
                "contrasena": partido.contrasena
            })
            db.commit()

        return partido

    def eliminar(self, partido_id: int) -> bool:
        """Elimina un partido"""
        sql = text("DELETE FROM partidos WHERE id = :partido_id")

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"partido_id": partido_id})
            db.commit()
            return result.rowcount > 0

    def buscar(
        self,
        titulo: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        tipo_futbol: Optional[TipoFutbol] = None,
        edad_minima: Optional[int] = None,
    ) -> List[Partido]:
        """Busca partidos según criterios"""
        sql_parts = [
            """
            SELECT 
                id, titulo, dinero_por_persona, descripcion, fecha_hora,
                latitud, longitud, ubicacion_texto, capacidad_maxima,
                organizador_id, tipo_partido, tipo_futbol, edad_minima,
                estado, contrasena
            FROM partidos
            WHERE 1=1
            """
        ]
        params = {}

        if titulo:
            sql_parts.append("AND LOWER(titulo) LIKE :titulo")
            params["titulo"] = f"%{titulo.lower()}%"

        if tipo_futbol:
            sql_parts.append("AND tipo_futbol = :tipo_futbol")
            params["tipo_futbol"] = tipo_futbol.value

        if edad_minima is not None:
            sql_parts.append("AND edad_minima <= :edad_minima")
            params["edad_minima"] = edad_minima

        if fecha_desde:
            sql_parts.append("AND fecha_hora >= :fecha_desde")
            params["fecha_desde"] = fecha_desde

        if fecha_hasta:
            sql_parts.append("AND fecha_hora <= :fecha_hasta")
            params["fecha_hasta"] = fecha_hasta

        sql = text(" ".join(sql_parts))

        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, params).fetchall()

        return [
            Partido(
                id=row.id,
                titulo=row.titulo,
                dinero_por_persona=row.dinero_por_persona,
                descripcion=row.descripcion,
                fecha_hora=row.fecha_hora,
                latitud=row.latitud,
                longitud=row.longitud,
                ubicacion_texto=row.ubicacion_texto,
                capacidad_maxima=row.capacidad_maxima,
                organizador_id=row.organizador_id,
                tipo_partido=TipoPartido(row.tipo_partido),
                tipo_futbol=TipoFutbol(row.tipo_futbol),
                edad_minima=row.edad_minima,
                estado=EstadoPartido(row.estado),
                contrasena=row.contrasena
            )
            for row in results
        ]