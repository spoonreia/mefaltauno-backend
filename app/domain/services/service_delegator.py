"""Delegador de servicios - Factory para instanciar servicios de dominio"""
from app.infra.database.database_service import DatabaseConnection
from app.domain.services.partidos import PartidoService
from app.domain.services.usuarios import UsuarioService
from app.domain.services.invitaciones import InvitacionService
from app.domain.services.repository_delegator import RepositoryDelegator


class ServiceDelegator:
    """
    Delegador para crear instancias de servicios de dominio.
    Centraliza la creación de servicios con sus dependencias inyectadas.
    """

    def __init__(self, database_client: DatabaseConnection):
        """
        Inicializa el delegador con el cliente de base de datos

        Args:
            database_client: Cliente de conexión a la base de datos
        """
        self.database_client = database_client
        self.repo_delegator = RepositoryDelegator(database_client)

    def get_partido_service(self) -> PartidoService:
        """
        Obtiene una instancia del servicio de partidos con sus dependencias

        Returns:
            PartidoService: Instancia del servicio de partidos
        """
        return PartidoService(
            partido_repo=self.repo_delegator.get_partido_repository(),
            usuario_repo=self.repo_delegator.get_usuario_repository(),
            participacion_repo=self.repo_delegator.get_participacion_repository(),
            invitacion_repo=self.repo_delegator.get_invitacion_repository(),
        )

    def get_usuario_service(self) -> UsuarioService:
        """
        Obtiene una instancia del servicio de usuarios con sus dependencias

        Returns:
            UsuarioService: Instancia del servicio de usuarios
        """
        return UsuarioService(
            usuario_repo=self.repo_delegator.get_usuario_repository(),
            database_client=self.database_client,
        )

    def get_invitacion_service(self) -> InvitacionService:
        """
        Obtiene una instancia del servicio de invitaciones con sus dependencias

        Returns:
            InvitacionService: Instancia del servicio de invitaciones
        """
        return InvitacionService(
            invitacion_repo=self.repo_delegator.get_invitacion_repository(),
            usuario_repo=self.repo_delegator.get_usuario_repository(),
            partido_repo=self.repo_delegator.get_partido_repository(),
            participacion_repo=self.repo_delegator.get_participacion_repository(),
        )

    def get_all_services(self) -> dict:
        """
        Obtiene un diccionario con todas las instancias de servicios

        Returns:
            dict: Diccionario con los servicios instanciados
        """
        return {
            'partido_service': self.get_partido_service(),
            'usuario_service': self.get_usuario_service(),
            'invitacion_service': self.get_invitacion_service(),
        }


# Singleton del delegador (opcional, para uso global)
_service_delegator_instance = None


def get_service_delegator(database_client: DatabaseConnection) -> ServiceDelegator:
    """
    Obtiene una instancia del delegador de servicios (patrón Singleton)

    Args:
        database_client: Cliente de base de datos

    Returns:
        ServiceDelegator: Instancia del delegador
    """
    global _service_delegator_instance
    if _service_delegator_instance is None:
        _service_delegator_instance = ServiceDelegator(database_client)
    return _service_delegator_instance