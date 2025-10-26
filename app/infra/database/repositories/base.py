"""Repositorio base con utilidades comunes"""
from typing import Dict, Any, Optional
from datetime import datetime


class BaseRepository:
    """Clase base para repositorios con métodos comunes"""

    def __init__(self, database_client):
        self.database_client = database_client

    @staticmethod
    def dict_to_object(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte un diccionario de datos a formato estándar"""
        return data

    @staticmethod
    def convert_datetime_to_naive(dt: Optional[datetime]) -> Optional[datetime]:
        """Convierte datetime con timezone a naive datetime"""
        if dt and dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt