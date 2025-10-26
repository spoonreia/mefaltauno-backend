"""Interface abstracta para repositorio de usuarios"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class UsuarioRepositoryInterface(ABC):
    """Interface para repositorio de usuarios"""

    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        pass

    @abstractmethod
    def actualizar(self, usuario_id: int, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un usuario en la base de datos"""
        pass

    @abstractmethod
    def actualizar_postulacion(self, usuario_id: int, postulacion: bool) -> None:
        """Actualiza el estado de postulación de un usuario"""
        pass