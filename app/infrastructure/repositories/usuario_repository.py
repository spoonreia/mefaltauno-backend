"""Repositorio de Usuarios"""
from typing import Optional
from app.domain.models.usuario import Usuario


class UsuarioRepository:
    """Repositorio de usuarios"""

    def __init__(self, db_storage):
        self.db = db_storage

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        return next(
            (u for u in self.db.usuarios_db if u.id == usuario_id), 
            None
        )

    def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario"""
        for idx, u in enumerate(self.db.usuarios_db):
            if u.id == usuario.id:
                self.db.usuarios_db[idx] = usuario
                return usuario
        return usuario