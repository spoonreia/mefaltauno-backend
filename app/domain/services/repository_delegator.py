"""Delegador de repositorios - Factory para instanciar repositorios"""
from app.infra.database.database_service import DatabaseConnection
from app.infra.database.repositories.partidos import PartidoRepository
from app.infra.database.repositories.usuarios import UsuarioRepository
from app.infra.database.repositories.participaciones import ParticipacionRepository
from app.infra.database.repositories.invitaciones import InvitacionRepository


class RepositoryDelegator:
    """
    Delegador para crear instancias de repositorios.
    Centraliza la creación de repositorios para facilitar testing y mantenimiento.
    """

    def __init__(self, database_client: DatabaseConnection):
        """
        Inicializa el delegador con el cliente de base de datos

        Args:
            database_client: Cliente de conexión a la base de datos
        """
        self.database_client = database_client

    def get_partido_repository(self) -> PartidoRepository:
        """Obtiene una instancia del repositorio de partidos"""
        return PartidoRepository(self.database_client)

    def get_usuario_repository(self) -> UsuarioRepository:
        """Obtiene una instancia del repositorio de usuarios"""
        return UsuarioRepository(self.database_client)

    def get_participacion_repository(self) -> ParticipacionRepository:
        """Obtiene una instancia del repositorio de participaciones"""
        return ParticipacionRepository(self.database_client)

    def get_invitacion_repository(self) -> InvitacionRepository:
        """Obtiene una instancia del repositorio de invitaciones"""
        return InvitacionRepository(self.database_client)

    def get_all_repositories(self) -> dict:
        """
        Obtiene un diccionario con todas las instancias de repositorios

        Returns:
            dict: Diccionario con los repositorios instanciados
        """
        return {
            'partido_repo': self.get_partido_repository(),
            'usuario_repo': self.get_usuario_repository(),
            'participacion_repo': self.get_participacion_repository(),
            'invitacion_repo': self.get_invitacion_repository(),
        }


# Singleton del delegador (opcional, para uso global)
_repository_delegator_instance = None


def get_repository_delegator(database_client: DatabaseConnection) -> RepositoryDelegator:
    """
    Obtiene una instancia del delegador de repositorios (patrón Singleton)

    Args:
        database_client: Cliente de base de datos

    Returns:
        RepositoryDelegator: Instancia del delegador
    """
    global _repository_delegator_instance
    if _repository_delegator_instance is None:
        _repository_delegator_instance = RepositoryDelegator(database_client)
    return _repository_delegator_instance