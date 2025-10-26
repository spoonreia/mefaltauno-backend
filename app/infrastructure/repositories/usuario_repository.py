"""Repositorio de Usuarios"""
from typing import Optional
from app.domain.models.usuario import Usuario
from app.infrastructure.database.database_service import DatabaseConnection
from app.domain.enums.estado import Genero, Posicion
from sqlalchemy import text


class UsuarioRepository:
    """Repositorio de usuarios"""

    def __init__(self, database_client: DatabaseConnection):
        super().__init__()
        self.database_client = database_client

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
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
                where u.id = :idUsuario;
            """
        )

        with self.database_client.get_session("tt") as db:
            result = db.execute(sql, {"idUsuario": usuario_id}).fetchone()
            if result is None:
                return None

        return Usuario(
            id=result.id,
            nombre=result.nombre,
            fechaNac=result.fecha_nacimiento,
            edad=result.edad,
            latitud=result.latitud,
            longitud=result.longitud,
            ubicacion_texto=result.ubicacion_texto,
            descripcion=result.descripcion,
            genero=Genero(result.genero),
            posicion=Posicion(result.posicion),
            postulado=result.postulado
        )

    def actualizar(self, usuario: Usuario) -> Usuario:
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

        with self.database_client.get_session("tt") as db:
            db.execute(sql, {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "fecha_nacimiento": usuario.fechaNac,
                "latitud": usuario.latitud,
                "longitud": usuario.longitud,
                "ubicacion_texto": usuario.ubicacion_texto,
                "descripcion": usuario.descripcion,
                "genero": usuario.genero.value,  # Convertir enum a string
                "posicion": usuario.posicion.value  # Convertir enum a string
            })
            db.commit()

        return usuario

    def actualizarPostulacion(self, usuario_id: int, postulacion: bool):
        """Actualiza un usuario en la base de datos"""
        sql = text(
            """
                UPDATE usuarios 
                SET 
                    postulado = :postulado
                WHERE id = :id
            """
        )

        with self.database_client.get_session("tt") as db:
            db.execute(sql, {
                "id": usuario_id,
                "postulado": postulacion,
            })
            db.commit()