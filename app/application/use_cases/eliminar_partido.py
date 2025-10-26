"""Caso de uso: Eliminar Partido"""
from app.domain.services.partido_service import PartidoService
from app.domain.exceptions.partido_exceptions import PartidoNoEncontradoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.repositories.invitacion_repository import InvitacionRepository
from app.infrastructure.database.database_service import DatabaseConnection


class EliminarPartidoUseCase:
    """Caso de uso para eliminar un partido"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)
        self.invitacion_repo = InvitacionRepository(database_client)
        self.partido_service = PartidoService()

    def execute(self, partido_id: int, organizador_id: int) -> dict:
        """Ejecuta el caso de uso"""

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # Validar permisos
        self.partido_service.validar_organizador(partido, organizador_id)

        # Validar tiempo
        if not self.partido_service.puede_eliminar_partido(partido):
            raise ValueError(
                "No se puede eliminar un partido con menos de 24 horas de anticipación"
            )

        # Eliminar participaciones
        self.participacion_repo.eliminar_por_partido(partido_id)

        # Eliminar invitaciones
        self.invitacion_repo.eliminar_por_partido(partido_id)

        # Eliminar partido
        self.partido_repo.eliminar(partido_id)

        return {
            "mensaje": "Partido eliminado correctamente",
            "partido_id": partido_id
        }