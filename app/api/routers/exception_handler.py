"""Manejador global de excepciones"""
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    DomainException,
    PartidoNoEncontradoException,
    PartidoCompletoException,
    ContrasenaIncorrectaException,
    UsuarioNoEncontradoException,
    ParticipacionNoEncontradaException,
    InvitacionNoEncontradaException,
    PermisosDenegadosException,
    CapacidadInvalidaException,
)


def configurar_exception_handlers(app):
    """Configura los manejadores de excepciones personalizadas"""

    @app.exception_handler(PartidoNoEncontradoException)
    async def partido_no_encontrado_handler(request: Request, exc: PartidoNoEncontradoException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "PartidoNoEncontrado", "mensaje": str(exc)}
        )

    @app.exception_handler(UsuarioNoEncontradoException)
    async def usuario_no_encontrado_handler(request: Request, exc: UsuarioNoEncontradoException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "UsuarioNoEncontrado", "mensaje": str(exc)}
        )

    @app.exception_handler(ParticipacionNoEncontradaException)
    async def participacion_no_encontrada_handler(request: Request, exc: ParticipacionNoEncontradaException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "ParticipacionNoEncontrada", "mensaje": str(exc)}
        )

    @app.exception_handler(InvitacionNoEncontradaException)
    async def invitacion_no_encontrada_handler(request: Request, exc: InvitacionNoEncontradaException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "InvitacionNoEncontrada", "mensaje": str(exc)}
        )

    @app.exception_handler(PartidoCompletoException)
    async def partido_completo_handler(request: Request, exc: PartidoCompletoException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "PartidoCompleto", "mensaje": str(exc)}
        )

    @app.exception_handler(ContrasenaIncorrectaException)
    async def contrasena_incorrecta_handler(request: Request, exc: ContrasenaIncorrectaException):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "ContrasenaIncorrecta", "mensaje": str(exc)}
        )

    @app.exception_handler(PermisosDenegadosException)
    async def permisos_denegados_handler(request: Request, exc: PermisosDenegadosException):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "PermisosDenegados", "mensaje": str(exc)}
        )

    @app.exception_handler(CapacidadInvalidaException)
    async def capacidad_invalida_handler(request: Request, exc: CapacidadInvalidaException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "CapacidadInvalida", "mensaje": str(exc)}
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "ErrorDeValidacion", "mensaje": str(exc)}
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "ErrorDeDominio", "mensaje": str(exc)}
        )