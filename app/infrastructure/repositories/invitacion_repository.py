"""Repositorio de Invitaciones"""
from typing import List, Optional
from datetime import datetime
from app.domain.models.invitacion import Invitacion
from app.domain.enums.estado import EstadoInvitacion
from app.infrastructure.database.database_service import DatabaseConnection
from sqlalchemy import text


class InvitacionRepository:
    """Repositorio de invitaciones conectado a la base de datos"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client

    def crear(self, invitacion: Invitacion) -> Invitacion:
        """Crea una nueva invitación (solo guarda IDs, no datos del partido)"""
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
            result = db.execute(sql, {
                "partido_id": invitacion.partido_id,
                "jugador_id": invitacion.jugador_id,
                "estado": invitacion.estado.value,
                "fecha_invitacion": invitacion.fecha_invitacion
            })
            db.commit()
            invitacion.id = result.lastrowid

        return invitacion

    def obtener_por_id(self, invitacion_id: int) -> Optional[Invitacion]:
        """Obtiene una invitación por ID con datos del partido mediante JOIN"""
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

        return Invitacion(
            id=result.id,
            partido_id=result.partido_id,
            partido_titulo=result.partido_titulo,
            partido_fecha_hora=result.partido_fecha_hora,
            partido_ubicacion=result.partido_ubicacion,
            jugador_id=result.jugador_id,
            estado=EstadoInvitacion(result.estado),
            fecha_invitacion=result.fecha_invitacion
        )

    def obtener_por_jugador(self, jugador_id: int, estado: Optional[EstadoInvitacion] = None) -> List[Invitacion]:
        """Obtiene todas las invitaciones de un jugador con datos del partido"""
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
            params["estado"] = estado.value

        sql_parts.append("ORDER BY i.fecha_invitacion DESC")

        sql = text(" ".join(sql_parts))

        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, params).fetchall()

        return [
            Invitacion(
                id=row.id,
                partido_id=row.partido_id,
                partido_titulo=row.partido_titulo,
                partido_fecha_hora=row.partido_fecha_hora,
                partido_ubicacion=row.partido_ubicacion,
                jugador_id=row.jugador_id,
                estado=EstadoInvitacion(row.estado),
                fecha_invitacion=row.fecha_invitacion
            )
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
            AND estado = :estado
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {
                "partido_id": partido_id,
                "jugador_id": jugador_id,
                "estado": EstadoInvitacion.PENDIENTE.value
            }).fetchone()

        return result.total > 0 if result else False

    def actualizar(self, invitacion: Invitacion) -> Invitacion:
        """Actualiza una invitación (solo el estado y fecha_respuesta)"""
        sql = text(
            """
            UPDATE invitaciones 
            SET 
                estado = :estado,
                fecha_respuesta = :fecha_respuesta
            WHERE id = :id
            """
        )

        with self.database_client.get_session("tt") as db:
            db.execute(sql, {
                "id": invitacion.id,
                "estado": invitacion.estado.value,
                "fecha_respuesta": datetime.now() if invitacion.estado != EstadoInvitacion.PENDIENTE else None
            })
            db.commit()

        return invitacion

    def eliminar_por_partido(self, partido_id: int) -> int:
        """Elimina todas las invitaciones de un partido"""
        sql = text("DELETE FROM invitaciones WHERE partido_id = :partido_id")

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"partido_id": partido_id})
            db.commit()
            return result.rowcount