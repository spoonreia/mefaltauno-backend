"""Caso de uso: Actualizar Postulación de Usuario"""
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class ActualizarPostulacionUseCase:

    def __init__(self):
        self.usuario_repo = UsuarioRepository(db_instance)

    def execute(self, usuario_id: int, activo: bool) -> dict:
        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Actualizar estado de postulación
        usuario.postulado = activo

        # Guardar cambios
        self.usuario_repo.actualizar(usuario)

        # Mensaje según acción
        mensaje = "Te has postulado correctamente. Ahora aparecerás en las búsquedas de jugadores." if activo else "Te has despostulado. Ya no aparecerás en las búsquedas de jugadores."

        return {
            "mensaje": mensaje,
            "usuario_id": usuario_id,
            "postulado": activo,
        }