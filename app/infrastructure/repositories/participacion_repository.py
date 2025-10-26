"""Repositorio de Participaciones"""
from typing import List, Optional
from datetime import datetime
from app.domain.models.participacion import Participacion
from app.domain.enums.estado import EstadoParticipacion
from app.infrastructure.database.database_service import DatabaseConnection
from sqlalchemy import text


class ParticipacionRepository:
    """Repositorio de participaciones conectado a la base de datos"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client

    def crear(self, participacion: Participacion) -> Participacion:
        """Crea una nueva participación"""
        sql = text(
            """
            INSERT INTO participaciones (
                partido_id, jugador_id, estado, fecha_postulacion
            ) VALUES (
                :partido_id, :jugador_id, :estado, :fecha_postulacion
            )
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": participacion.partido_id,
                "jugador_id": participacion.jugador_id,
                "estado": participacion.estado.value,
                "fecha_postulacion": participacion.fecha_postulacion
            })
            db.commit()
            participacion.id = result.lastrowid

        return participacion

    def obtener_por_id(self, participacion_id: int) -> Optional[Participacion]:
        """Obtiene una participación por ID con el nombre del jugador"""
        sql = text(
            """
            SELECT 
                p.id, 
                p.partido_id, 
                p.jugador_id, 
                u.nombre as jugador_nombre,
                p.estado, 
                p.fecha_postulacion
            FROM participaciones p
            INNER JOIN usuarios u ON p.jugador_id = u.id
            WHERE p.id = :participacion_id
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"participacion_id": participacion_id}).fetchone()
            if result is None:
                return None

        return Participacion(
            id=result.id,
            partido_id=result.partido_id,
            jugador_id=result.jugador_id,
            jugador_nombre=result.jugador_nombre,
            estado=EstadoParticipacion(result.estado),
            fecha_postulacion=result.fecha_postulacion
        )

    def obtener_por_partido_y_jugador(self, partido_id: int, jugador_id: int) -> Optional[Participacion]:
        """Obtiene una participación por partido y jugador con el nombre del jugador"""
        sql = text(
            """
            SELECT 
                p.id, 
                p.partido_id, 
                p.jugador_id, 
                u.nombre as jugador_nombre,
                p.estado, 
                p.fecha_postulacion
            FROM participaciones p
            INNER JOIN usuarios u ON p.jugador_id = u.id
            WHERE p.partido_id = :partido_id AND p.jugador_id = :jugador_id
            ORDER BY p.fecha_postulacion DESC
            LIMIT 1
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": partido_id,
                "jugador_id": jugador_id
            }).fetchone()
            if result is None:
                return None

        return Participacion(
            id=result.id,
            partido_id=result.partido_id,
            jugador_id=result.jugador_id,
            jugador_nombre=result.jugador_nombre,
            estado=EstadoParticipacion(result.estado),
            fecha_postulacion=result.fecha_postulacion
        )

    def obtener_por_partido(self, partido_id: int) -> List[Participacion]:
        """Obtiene todas las participaciones de un partido con los nombres de jugadores"""
        sql = text(
            """
            SELECT 
                p.id, 
                p.partido_id, 
                p.jugador_id, 
                u.nombre as jugador_nombre,
                p.estado, 
                p.fecha_postulacion
            FROM participaciones p
            INNER JOIN usuarios u ON p.jugador_id = u.id
            WHERE p.partido_id = :partido_id
            ORDER BY p.fecha_postulacion ASC
            """
        )

        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, {"partido_id": partido_id}).fetchall()

        return [
            Participacion(
                id=row.id,
                partido_id=row.partido_id,
                jugador_id=row.jugador_id,
                jugador_nombre=row.jugador_nombre,
                estado=EstadoParticipacion(row.estado),
                fecha_postulacion=row.fecha_postulacion
            )
            for row in results
        ]

    def contar_por_estado(self, partido_id: int, estado: EstadoParticipacion) -> int:
        """Cuenta participaciones por estado en un partido"""
        sql = text(
            """
            SELECT COUNT(*) as total
            FROM participaciones
            WHERE partido_id = :partido_id AND estado = :estado
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": partido_id,
                "estado": estado.value
            }).fetchone()

        return result.total if result else 0

    def actualizar(self, participacion: Participacion) -> Participacion:
        """Actualiza una participación (solo el estado, el nombre viene de usuarios)"""
        sql = text(
            """
            UPDATE participaciones 
            SET estado = :estado
            WHERE id = :id
            """
        )

        with self.database_client.get_session("tt") as db:
            db.execute(sql, {
                "id": participacion.id,
                "estado": participacion.estado.value
            })
            db.commit()

        return participacion

    def eliminar_por_partido(self, partido_id: int) -> int:
        """Elimina todas las participaciones de un partido"""
        sql = text("DELETE FROM participaciones WHERE partido_id = :partido_id")

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"partido_id": partido_id})
            db.commit()
            return result.rowcount

    def existe_participacion_activa(self, partido_id: int, jugador_id: int) -> bool:
        """Verifica si existe una participación activa"""
        sql = text(
            """
            SELECT COUNT(*) as total
            FROM participaciones
            WHERE partido_id = :partido_id 
            AND jugador_id = :jugador_id
            AND estado IN (:confirmado, :pendiente)
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": partido_id,
                "jugador_id": jugador_id,
                "confirmado": EstadoParticipacion.CONFIRMADO.value,
                "pendiente": EstadoParticipacion.PENDIENTE.value
            }).fetchone()

        return result.total > 0 if result else False