"""Interface abstracta para repositorio de partidos"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class PartidoRepositoryInterface(ABC):
    """Interface para repositorio de partidos"""

    @abstractmethod
    def crear(self, partido_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo partido"""
        pass

    @abstractmethod
    def obtener_por_id(self, partido_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un partido por ID"""
        pass

    @abstractmethod
    def actualizar(self, partido_id: int, partido_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un partido existente"""
        pass

    @abstractmethod
    def eliminar(self, partido_id: int) -> bool:
        """Elimina un partido"""
        pass

    @abstractmethod
    def buscar(
            self,
            titulo: Optional[str] = None,
            fecha_desde: Optional[datetime] = None,
            fecha_hasta: Optional[datetime] = None,
            tipo_futbol: Optional[str] = None,
            edad_minima: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Busca partidos según criterios"""
        pass