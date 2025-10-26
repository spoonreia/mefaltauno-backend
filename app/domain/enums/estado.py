"""Enumeraciones del dominio"""
from enum import Enum


class TipoPartido(str, Enum):
    PUBLICO = "Publico"
    PRIVADO = "Privado"


class TipoFutbol(str, Enum):
    FUTBOL_5 = "Futbol 5"
    FUTBOL_7 = "Futbol 7"
    FUTBOL_11 = "Futbol 11"


class EstadoPartido(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"
    FINALIZADO = "Finalizado"


class EstadoParticipacion(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADO = "Confirmado"
    RECHAZADO = "Rechazado"
    CANCELADO = "Cancelado"


class EstadoInvitacion(str, Enum):
    PENDIENTE = "Pendiente"
    ACEPTADA = "Aceptada"
    RECHAZADA = "Rechazada"

class Genero(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    NO_DEFINIDO = "Otro"


class Posicion(str, Enum):
    ARQUERO = "Arquero"
    DEFENSA = "Defensa"
    MEDIOCAMPISTA = "Mediocampista"
    DELANTERO = "Delantero"