"""Constantes de la aplicación"""

# Base de datos
DB_POOL_SIZE: int = 2
DB_POOL_MAX_SIZE: int = 5
DB_LOG_QUERY: bool = False
DB_CONNECTION_RECYCLE: int = 3600

# Distancias
RADIO_TIERRA_KM: float = 6371.0

# Límites
MIN_EDAD_PARTIDO: int = 16
MAX_EDAD_PARTIDO: int = 99
MIN_CAPACIDAD_PARTIDO: int = 2
MAX_CAPACIDAD_PARTIDO: int = 22
HORAS_MINIMAS_ELIMINAR_PARTIDO: int = 24

# Distancias por defecto
DISTANCIA_MAXIMA_BUSQUEDA_KM: float = 5.0
DISTANCIA_MAXIMA_JUGADORES_KM: float = 10.0

# Calendarios
DIAS_CALENDARIO_FUTURO: int = 30