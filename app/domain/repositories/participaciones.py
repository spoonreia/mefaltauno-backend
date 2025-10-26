"""Interface abstracta para repositorio de participaciones"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class ParticipacionRepositoryInterface(ABC):
    """Interface para repositorio de participaciones"""

    @abstractmethod
    def crear(self, participacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva participación"""
        pass

    @abstractmethod
    def obtener_por_id(self, participacion_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una participación por ID"""
        pass

    @abstractmethod
    def obtener_por_partido_y_jugador(
            self, partido_id: int, jugador_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene una participación por partido y jugador"""
        pass

    @abstractmethod
    def obtener_por_partido(self, partido_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las participaciones de un partido"""
        pass

    @abstractmethod
    def contar_por_estado(self, partido_id: int, estado: str) -> int:
        """Cuenta participaciones por estado en un partido"""
        pass

    @abstractmethod
    def actualizar(self, participacion_id: int, participacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una participación"""
        pass

    @abstractmethod
    def eliminar_por_partido(self, partido_id: int) -> int:
        """Elimina todas las participaciones de un partido"""
        pass

    @abstractmethod
    def existe_participacion_activa(self, partido_id: int, jugador_id: int) -> bool:
        """Verifica si existe una participación activa"""
        pass