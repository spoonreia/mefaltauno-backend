"""Excepciones personalizadas del dominio"""


# ============================================
# EXCEPCIÓN BASE
# ============================================

class DomainException(Exception):
    """Excepción base para errores del dominio"""
    pass


# ============================================
# EXCEPCIONES DE PARTIDOS
# ============================================

class PartidoException(DomainException):
    """Excepción base para errores relacionados con partidos"""
    pass


class PartidoNoEncontradoException(PartidoException):
    """El partido no existe"""
    pass


class PartidoCompletoException(PartidoException):
    """El partido ya está completo"""
    pass


class ContrasenaIncorrectaException(PartidoException):
    """La contraseña del partido es incorrecta"""
    pass


# ============================================
# EXCEPCIONES DE USUARIOS
# ============================================

class UsuarioException(DomainException):
    """Excepción base para errores relacionados con usuarios"""
    pass


class UsuarioNoEncontradoException(UsuarioException):
    """El usuario no existe"""
    pass


# ============================================
# EXCEPCIONES DE PARTICIPACIONES
# ============================================

class ParticipacionException(DomainException):
    """Excepción base para errores relacionados con participaciones"""
    pass


class ParticipacionNoEncontradaException(ParticipacionException):
    """La participación no existe"""
    pass


# ============================================
# EXCEPCIONES DE INVITACIONES
# ============================================

class InvitacionException(DomainException):
    """Excepción base para errores relacionados con invitaciones"""
    pass


class InvitacionNoEncontradaException(InvitacionException):
    """La invitación no existe"""
    pass


# ============================================
# EXCEPCIONES DE PERMISOS
# ============================================

class PermisoException(DomainException):
    """Excepción base para errores de permisos"""
    pass


class PermisosDenegadosException(PermisoException):
    """El usuario no tiene permisos para esta acción"""
    pass


# ============================================
# EXCEPCIONES DE VALIDACIÓN
# ============================================

class ValidacionException(DomainException):
    """Excepción base para errores de validación"""
    pass


class CapacidadInvalidaException(ValidacionException):
    """La capacidad es menor a los jugadores confirmados"""
    pass