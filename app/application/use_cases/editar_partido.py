"""Caso de uso: Editar Partido"""
from typing import Optional
from app.domain.services.partido_service import PartidoService
from app.domain.exceptions.partido_exceptions import PartidoNoEncontradoException
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.in_memory_db import db_instance
from app.domain.enums.estado import EstadoParticipacion


class EditarPartidoUseCase:
    """Caso de uso para editar un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.partido_service = PartidoService()

    def execute(
        self,
        partido_id: int,
        organizador_id: int,
        dinero_por_persona: Optional[int] = None,
        descripcion: Optional[str] = None,
        latitud: Optional[float] = None,
        longitud: Optional[float] = None,
        ubicacion_texto: Optional[str] = None,
        capacidad_maxima: Optional[int] = None,
        edad_minima: Optional[int] = None,
        contrasena: Optional[str] = None,
    ):
        """Ejecuta el caso de uso"""

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException("Partido no encontrado")

        # Validar permisos
        self.partido_service.validar_organizador(partido, organizador_id)

        # Actualizar campos
        if dinero_por_persona is not None:
            partido.dinero_por_persona = dinero_por_persona

        if descripcion is not None:
            partido.descripcion = descripcion

        if latitud is not None:
            partido.latitud = latitud

        if longitud is not None:
            partido.longitud = longitud

        if ubicacion_texto is not None:
            partido.ubicacion_texto = ubicacion_texto

        if capacidad_maxima is not None:
            confirmados = len([
                p for p in db_instance.participaciones_db
                if p.partido_id == partido_id and p.estado == EstadoParticipacion.CONFIRMADO
            ])
            self.partido_service.validar_capacidad(capacidad_maxima, confirmados)
            partido.capacidad_maxima = capacidad_maxima

        if edad_minima is not None:
            partido.edad_minima = edad_minima

        # Gestionar privacidad
        if contrasena is not None:
            partido = self.partido_service.gestionar_privacidad(partido, contrasena)

        # Actualizar en repositorio
        return self.partido_repo.actualizar(partido)