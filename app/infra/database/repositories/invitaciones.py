"""Implementación del repositorio de Invitaciones"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text

from app.domain.repositories.invitaciones import InvitacionRepositoryInterface
from app.infra.database.repositories.base import BaseRepository


class InvitacionRepository(BaseRepository, InvitacionRepositoryInterface):
    """Repositorio de invitaciones conectado a MySQL"""

    def crear(self, invitacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva invitación"""
        sql = text(
            """
            INSERT INTO invitaciones (
                partido_id, jugador_id, estado, fecha_invitacion
            ) VALUES (
                :partido_id, :jugador_id, :estado, :fecha_invitacion
            )
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, invitacion_data)
            db.commit()
            invitacion_data['id'] = result.lastrowid

        return invitacion_data

    def obtener_por_id(self, invitacion_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una invitación por ID con datos del partido"""
        sql = text(
            """
            SELECT 
                i.id,
                i.partido_id,
                p.titulo as partido_titulo,
                p.fecha_hora as partido_fecha_hora,
                p.ubicacion_texto as partido_ubicacion,
                i.jugador_id,
                i.estado,
                i.fecha_invitacion
            FROM invitaciones i
            INNER JOIN partidos p ON i.partido_id = p.id
            WHERE i.id = :invitacion_id
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"invitacion_id": invitacion_id}).fetchone()
            if result is None:
                return None

        return {
            'id': result.id,
            'partido_id': result.partido_id,
            'partido_titulo': result.partido_titulo,
            'partido_fecha_hora': result.partido_fecha_hora,
            'partido_ubicacion': result.partido_ubicacion,
            'jugador_id': result.jugador_id,
            'estado': result.estado,
            'fecha_invitacion': result.fecha_invitacion
        }

    def obtener_por_jugador(
        self, jugador_id: int, estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene todas las invitaciones de un jugador"""
        sql_parts = [
            """
            SELECT 
                i.id,
                i.partido_id,
                p.titulo as partido_titulo,
                p.fecha_hora as partido_fecha_hora,
                p.ubicacion_texto as partido_ubicacion,
                i.jugador_id,
                i.estado,
                i.fecha_invitacion
            FROM invitaciones i
            INNER JOIN partidos p ON i.partido_id = p.id
            WHERE i.jugador_id = :jugador_id
            """
        ]
        params = {"jugador_id": jugador_id}

        if estado:
            sql_parts.append("AND i.estado = :estado")
            params["estado"] = estado

        sql_parts.append("ORDER BY i.fecha_invitacion DESC")

        sql = text(" ".join(sql_parts))

        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, params).fetchall()

        return [
            {
                'id': row.id,
                'partido_id': row.partido_id,
                'partido_titulo': row.partido_titulo,
                'partido_fecha_hora': row.partido_fecha_hora,
                'partido_ubicacion': row.partido_ubicacion,
                'jugador_id': row.jugador_id,
                'estado': row.estado,
                'fecha_invitacion': row.fecha_invitacion
            }
            for row in results
        ]

    def existe_invitacion_pendiente(self, partido_id: int, jugador_id: int) -> bool:
        """Verifica si existe una invitación pendiente"""
        sql = text(
            """
            SELECT COUNT(*) as total
            FROM invitaciones
            WHERE partido_id = :partido_id 
            AND jugador_id = :jugador_id
            AND estado = 'Pendiente'
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": partido_id,
                "jugador_id": jugador_id
            }).fetchone()

        return result.total > 0 if result else False

    def actualizar(self, invitacion_id: int, invitacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una invitación"""
        sql = text(
            """
            UPDATE invitaciones 
            SET 
                estado = :estado,
                fecha_respuesta = :fecha_respuesta
            WHERE id = :id
            """
        )

        invitacion_data['id'] = invitacion_id
        if 'fecha_respuesta' not in invitacion_data:
            invitacion_data['fecha_respuesta'] = datetime.now() if invitacion_data.get('estado') != 'Pendiente' else None

        with self.database_client.get_session("tt") as db:
            db.execute(sql, invitacion_data)
            db.commit()

        return invitacion_data

    def eliminar_por_partido(self, partido_id: int) -> int:
        """Elimina todas las invitaciones de un partido"""
        sql = text("DELETE FROM invitaciones WHERE partido_id = :partido_id")

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"partido_id": partido_id})
            db.commit()
            return result.rowcount