# TEMPORALY IN-MEMORY DB FOR DEMO PURPOSES ONLY

"""Base de datos en memoria (temporal)"""
from datetime import datetime, timedelta
from app.domain.enums.estado import (
    TipoPartido,
    TipoFutbol,
    EstadoPartido,
    EstadoParticipacion,
    Genero,
    Posicion,
)
from app.domain.models.usuario import Usuario
from app.domain.models.participacion import Participacion


class InMemoryDatabase:
    """Almacenamiento en memoria"""

    def __init__(self):
        self.usuarios_db = [
            Usuario(
                id=1,
                nombre="Juan Pérez",
                edad=28,
                latitud=-34.7050,
                longitud=-58.5648,
                ubicacion_texto="Morón, Buenos Aires",
                descripcion="Jugador amateur, me gusta el fútbol desde chico",
                genero=Genero.MASCULINO,
                posicion=Posicion.MEDIOCAMPISTA,
                postulado=False,
            ),
            Usuario(
                id=2,
                nombre="María González",
                edad=25,
                latitud=-34.6764,
                longitud=-58.5640,
                ubicacion_texto="Castelar, Buenos Aires",
                descripcion="Delantero, juego hace 10 años",
                genero=Genero.FEMENINO,
                posicion=Posicion.DELANTERO,
                postulado=True,  # Postulada para ser invitada
            ),
            Usuario(
                id=3,
                nombre="Carlos Rodríguez",
                edad=32,
                latitud=-34.6590,
                longitud=-58.6227,
                ubicacion_texto="Ituzaingó, Buenos Aires",
                descripcion="Arquero experimentado",
                genero=Genero.MASCULINO,
                posicion=Posicion.ARQUERO,
                postulado=True,  # Postulado para ser invitado
            ),
            Usuario(
                id=4,
                nombre="Laura Martínez",
                edad=23,
                latitud=-34.7100,
                longitud=-58.5700,
                ubicacion_texto="Morón, Buenos Aires",
                descripcion="Defensora rápida",
                genero=Genero.FEMENINO,
                posicion=Posicion.DEFENSA,
                postulado=True,
            ),
            Usuario(
                id=5,
                nombre="Alex Torres",
                edad=27,
                latitud=-34.6800,
                longitud=-58.5800,
                ubicacion_texto="Castelar, Buenos Aires",
                descripcion="Juego en cualquier posición",
                genero=Genero.NO_DEFINIDO,
                posicion=Posicion.MEDIOCAMPISTA,
                postulado=False,
            ),
        ]

        self.partidos_db = [
            {
                "id": 1,
                "titulo": "Futbol 5 - Sábado tarde",
                "dinero_por_persona": 5000,
                "descripcion": "Partido tranquilo para pasar el rato",
                "fecha_hora": datetime.now().replace(
                    hour=19, minute=0, second=0, microsecond=0
                )
                + timedelta(days=2, hours=3),
                "latitud": -34.7050,
                "longitud": -58.5648,
                "ubicacion_texto": "Complejo La Cancha, Morón",
                "capacidad_maxima": 10,
                "organizador_id": 1,
                "tipo_partido": TipoPartido.PUBLICO,
                "tipo_futbol": TipoFutbol.FUTBOL_5,
                "edad_minima": 18,
                "estado": EstadoPartido.PENDIENTE,
                "contrasena": None,
            },
        ]

        self.participaciones_db = [
            Participacion(
                id=1,
                partido_id=1,
                jugador_id=1,
                jugador_nombre="Juan Pérez",
                estado=EstadoParticipacion.CONFIRMADO,
                fecha_postulacion=datetime.now() - timedelta(hours=5),
            ),
        ]

        self.invitaciones_db = []


# Instancia global (singleton temporal)
db_instance = InMemoryDatabase()