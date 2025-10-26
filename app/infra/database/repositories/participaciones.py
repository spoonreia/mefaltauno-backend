"""Implementación del repositorio de Participaciones"""
from typing import List, Optional, Dict, Any
from sqlalchemy import text

from app.domain.repositories.participaciones import ParticipacionRepositoryInterface
from app.infra.database.repositories.base import BaseRepository


class ParticipacionRepository(BaseRepository, ParticipacionRepositoryInterface):
    """Repositorio de participaciones conectado a MySQL"""

    def crear(self, participacion_data: Dict[str, Any]) -> Dict[str, Any]:
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
            result = db.execute(sql, participacion_data)
            db.commit()
            participacion_data['id'] = result.lastrowid

        return participacion_data

    def obtener_por_id(self, participacion_id: int) -> Optional[Dict[str, Any]]:
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

        return {
            'id': result.id,
            'partido_id': result.partido_id,
            'jugador_id': result.jugador_id,
            'jugador_nombre': result.jugador_nombre,
            'estado': result.estado,
            'fecha_postulacion': result.fecha_postulacion
        }

    def obtener_por_partido_y_jugador(
        self, partido_id: int, jugador_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene una participación por partido y jugador"""
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

        return {
            'id': result.id,
            'partido_id': result.partido_id,
            'jugador_id': result.jugador_id,
            'jugador_nombre': result.jugador_nombre,
            'estado': result.estado,
            'fecha_postulacion': result.fecha_postulacion
        }

    def obtener_por_partido(self, partido_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las participaciones de un partido"""
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
            {
                'id': row.id,
                'partido_id': row.partido_id,
                'jugador_id': row.jugador_id,
                'jugador_nombre': row.jugador_nombre,
                'estado': row.estado,
                'fecha_postulacion': row.fecha_postulacion
            }
            for row in results
        ]

    def contar_por_estado(self, partido_id: int, estado: str) -> int:
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
                "estado": estado
            }).fetchone()

        return result.total if result else 0

    def actualizar(self, participacion_id: int, participacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una participación"""
        sql = text(
            """
            UPDATE participaciones 
            SET estado = :estado
            WHERE id = :id
            """
        )

        participacion_data['id'] = participacion_id

        with self.database_client.get_session("tt") as db:
            db.execute(sql, participacion_data)
            db.commit()

        return participacion_data

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
            AND estado IN ('Confirmado', 'Pendiente')
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": partido_id,
                "jugador_id": jugador_id
            }).fetchone()

        return result.total > 0 if result else False