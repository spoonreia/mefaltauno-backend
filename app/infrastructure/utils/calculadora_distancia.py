"""Utilidad para calcular distancia entre coordenadas"""
import math


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
    R = 6371  # Radio de la Tierra en kilómetros
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2 + 
        math.cos(math.radians(lat1)) * 
        math.cos(math.radians(lat2)) * 
        math.sin(dlon / 2) ** 2
    )
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return round(R * c, 2)