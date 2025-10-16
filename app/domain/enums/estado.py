"""Enumeraciones del dominio"""
from enum import Enum


class TipoPartido(str, Enum):
    PUBLICO = "PUBLICO"
    PRIVADO = "PRIVADO"


class TipoFutbol(str, Enum):
    FUTBOL_5 = "FUTBOL_5"
    FUTBOL_7 = "FUTBOL_7"
    FUTBOL_11 = "FUTBOL_11"


class EstadoPartido(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"
    FINALIZADO = "FINALIZADO"


class EstadoParticipacion(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    RECHAZADO = "RECHAZADO"
    CANCELADO = "CANCELADO"


class EstadoInvitacion(str, Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    RECHAZADA = "RECHAZADA"