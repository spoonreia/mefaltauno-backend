"""Implementación del repositorio de Usuarios"""
from typing import Optional, Dict, Any
from sqlalchemy import text

from app.domain.repositories.usuarios import UsuarioRepositoryInterface
from app.infra.database.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository, UsuarioRepositoryInterface):
    """Repositorio de usuarios conectado a MySQL"""

    def obtener_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        sql = text(
            """
            SELECT 
                u.id, 
                u.nombre, 
                TIMESTAMPDIFF(YEAR, u.fecha_nacimiento, CURDATE()) as edad,
                u.fecha_nacimiento,
                u.latitud,
                u.longitud,
                u.ubicacion_texto,
                u.descripcion,
                u.genero,
                u.posicion,
                u.postulado
            FROM usuarios u
            WHERE u.id = :idUsuario
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"idUsuario": usuario_id}).fetchone()
            if result is None:
                return None

        return {
            'id': result.id,
            'nombre': result.nombre,
            'edad': result.edad,
            'fechaNac': result.fecha_nacimiento,
            'latitud': result.latitud,
            'longitud': result.longitud,
            'ubicacion_texto': result.ubicacion_texto,
            'descripcion': result.descripcion,
            'genero': result.genero,
            'posicion': result.posicion,
            'postulado': result.postulado
        }

    def actualizar(self, usuario_id: int, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un usuario en la base de datos"""
        sql = text(
            """
            UPDATE usuarios 
            SET 
                nombre = :nombre,
                fecha_nacimiento = :fecha_nacimiento,
                latitud = :latitud,
                longitud = :longitud,
                ubicacion_texto = :ubicacion_texto,
                descripcion = :descripcion,
                genero = :genero,
                posicion = :posicion
            WHERE id = :id
            """
        )

        usuario_data['id'] = usuario_id

        with self.database_client.get_session("tt") as db:
            db.execute(sql, usuario_data)
            db.commit()

        return usuario_data

    def actualizar_postulacion(self, usuario_id: int, postulacion: bool) -> None:
        """Actualiza el estado de postulación de un usuario"""
        sql = text(
            """
            UPDATE usuarios 
            SET postulado = :postulado
            WHERE id = :id
            """
        )

        with self.database_client.get_session("tt") as db:
            db.execute(sql, {
                "id": usuario_id,
                "postulado": postulacion,
            })
            db.commit()