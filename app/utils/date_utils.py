"""Utilidades para manejo de fechas, distancias y texto"""
import math
import unicodedata
from datetime import datetime, timezone, timedelta
from app.utils.constants import RADIO_TIERRA_KM


def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine

    Args:
        lat1: Latitud del punto 1
        lon1: Longitud del punto 1
        lat2: Latitud del punto 2
        lon2: Longitud del punto 2

    Returns:
        float: Distancia en kilómetros
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(RADIO_TIERRA_KM * c, 2)


def normalizar_texto(texto: str) -> str:
    # Convertir a minúsculas
    texto = texto.lower()

    # Remover acentos (NFD = Normalización de Descomposición Canónica)
    texto_nfd = unicodedata.normalize('NFD', texto)

    # Filtrar solo caracteres que no sean marcas de combinación (acentos)
    texto_sin_acentos = ''.join(
        char for char in texto_nfd
        if unicodedata.category(char) != 'Mn'  # Mn = Nonspacing_Mark
    )

    return texto_sin_acentos


def convertir_a_fecha_local(fecha_hora: datetime) -> datetime:
    if fecha_hora.tzinfo:
        tz_argentina = timezone(timedelta(hours=-3))
        fecha_hora_local = fecha_hora.astimezone(tz_argentina)
    else:
        fecha_hora_local = fecha_hora

    return fecha_hora_local.replace(tzinfo=None)


def calcular_edad(fecha_nacimiento: datetime) -> int:
    hoy = datetime.now().date()
    if isinstance(fecha_nacimiento, datetime):
        fecha_nacimiento = fecha_nacimiento.date()

    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1

    return edad