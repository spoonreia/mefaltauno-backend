"""Interface abstracta para repositorio de invitaciones"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class InvitacionRepositoryInterface(ABC):
    """Interface para repositorio de invitaciones"""

    @abstractmethod
    def crear(self, invitacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva invitación"""
        pass

    @abstractmethod
    def obtener_por_id(self, invitacion_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una invitación por ID"""
        pass

    @abstractmethod
    def obtener_por_jugador(
            self, jugador_id: int, estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene todas las invitaciones de un jugador"""
        pass

    @abstractmethod
    def existe_invitacion_pendiente(self, partido_id: int, jugador_id: int) -> bool:
        """Verifica si existe una invitación pendiente"""
        pass

    @abstractmethod
    def actualizar(self, invitacion_id: int, invitacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una invitación"""
        pass

    @abstractmethod
    def eliminar_por_partido(self, partido_id: int) -> int:
        """Elimina todas las invitaciones de un partido"""
        pass