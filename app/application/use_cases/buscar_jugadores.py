"""Caso de uso: Buscar Jugadores Disponibles para Invitar"""
from typing import List, Optional
from app.domain.enums.estado import Genero, Posicion
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance
from app.infrastructure.utils.calculadora_distancia import calcular_distancia
from app.infrastructure.utils.text_utils import normalizar_texto


class BuscarJugadoresDisponiblesUseCase:
    """Caso de uso para buscar jugadores postulados disponibles para invitar"""

    def __init__(self):
        self.usuario_repo = UsuarioRepository(db_instance)

    def execute(
        self,
        organizador_id: int,
        genero: Optional[Genero] = None,
        posicion: Optional[Posicion] = None,
        ubicacion_texto: Optional[str] = None,
        distancia_maxima_km: float = 10.0,
    ) -> List[dict]:
        """
        Ejecuta el caso de uso

        Args:
            organizador_id: ID del usuario que busca jugadores
            genero: Filtro por género (opcional)
            posicion: Filtro por posición (opcional)
            ubicacion_texto: Filtro por texto de ubicación (opcional)
            distancia_maxima_km: Distancia máxima en km (default 10km)

        Returns:
            Lista de jugadores disponibles con distancia
        """
        # Obtener organizador para calcular distancias
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise ValueError("Organizador no encontrado")

        # Normalizar texto de búsqueda si existe
        ubicacion_normalizada = normalizar_texto(ubicacion_texto) if ubicacion_texto else None

        # Obtener todos los usuarios postulados
        jugadores_postulados = [
            u for u in db_instance.usuarios_db
            if u.postulado and u.id != organizador_id  # Excluir al mismo organizador
        ]

        # Aplicar filtros y calcular distancias
        resultados = []
        for jugador in jugadores_postulados:
            # Filtro por género
            if genero and jugador.genero != genero:
                continue

            # Filtro por posición
            if posicion and jugador.posicion != posicion:
                continue

            # Filtro por ubicación (búsqueda parcial, case & accent insensitive)
            if ubicacion_normalizada:
                jugador_ubicacion_normalizada = normalizar_texto(jugador.ubicacion_texto)
                if ubicacion_normalizada not in jugador_ubicacion_normalizada:
                    continue

            # Calcular distancia
            distancia = calcular_distancia(
                organizador.latitud,
                organizador.longitud,
                jugador.latitud,
                jugador.longitud,
            )

            # Filtrar por distancia máxima
            if distancia > distancia_maxima_km:
                continue

            # Agregar a resultados
            resultado = {
                "id": jugador.id,
                "nombre": jugador.nombre,
                "posicion": jugador.posicion,
                "genero": jugador.genero,
                "edad": jugador.edad,
                "ubicacion_texto": jugador.ubicacion_texto,
                "distancia_km": distancia,
            }
            resultados.append(resultado)

        # Ordenar por distancia (más cercanos primero)
        resultados.sort(key=lambda x: x["distancia_km"])

        return resultados