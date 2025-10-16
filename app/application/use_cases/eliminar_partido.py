"""Caso de uso: Eliminar Partido"""
from datetime import datetime
from app.domain.services.partido_service import PartidoService
from app.domain.exceptions.partido_exceptions import (
    PartidoNoEncontradoException,
    PermisosDenegadosException,
)
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class EliminarPartidoUseCase:
    """Caso de uso para eliminar un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
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
        db_instance.participaciones_db = [
            p for p in db_instance.participaciones_db 
            if p.partido_id != partido_id
        ]

        # Eliminar invitaciones
        db_instance.invitaciones_db = [
            i for i in db_instance.invitaciones_db 
            if i.partido_id != partido_id
        ]

        # Eliminar partido
        self.partido_repo.eliminar(partido_id)

        return {
            "mensaje": "Partido eliminado correctamente",
            "partido_id": partido_id
        }