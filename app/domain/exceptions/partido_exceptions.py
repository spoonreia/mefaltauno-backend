"""Excepciones personalizadas del dominio"""


class PartidoException(Exception):
    """Excepción base para errores relacionados con partidos"""
    pass


class PartidoNoEncontradoException(PartidoException):
    """El partido no existe"""
    pass


class PermisosDenegadosException(PartidoException):
    """El usuario no tiene permisos para esta acción"""
    pass


class PartidoCompletoException(PartidoException):
    """El partido ya está completo"""
    pass


class ContrasenaIncorrectaException(PartidoException):
    """La contraseña del partido es incorrecta"""
    pass


class CapacidadInvalidaException(PartidoException):
    """La capacidad es menor a los jugadores confirmados"""
    pass