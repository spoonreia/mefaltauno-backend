"""Caso de uso: Actualizar Postulación de Usuario"""
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.database.database_service import DatabaseConnection


class ActualizarPostulacionUseCase:

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.usuario_repo = UsuarioRepository(database_client)

    def execute(self, usuario_id: int, activo: bool) -> dict:
        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Guardar cambios
        self.usuario_repo.actualizarPostulacion(usuario_id, activo)

        # Mensaje según acción
        mensaje = (
            "Te has postulado correctamente. Ahora aparecerás en las búsquedas de jugadores."
            if activo
            else "Te has despostulado. Ya no aparecerás en las búsquedas de jugadores."
        )

        return {
            "mensaje": mensaje,
            "usuario_id": usuario_id,
            "postulado": activo,
        }