"""Caso de uso: Buscar Jugadores Disponibles para Invitar"""
from typing import List, Optional
from app.domain.enums.estado import Genero, Posicion
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.database.database_service import DatabaseConnection
from app.infrastructure.utils.calculadora_distancia import calcular_distancia
from app.infrastructure.utils.text_utils import normalizar_texto
from sqlalchemy import text


class BuscarJugadoresDisponiblesUseCase:
    """Caso de uso para buscar jugadores postulados disponibles para invitar"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.usuario_repo = UsuarioRepository(database_client)

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
        # Obtener organizador para calcular distancias -- ESTA MAL; DEBERIA SER LA LAT Y LONG DEL PARTIDO, NO DEL ORGANIZADOR.
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise ValueError("Organizador no encontrado")

        # Construir query SQL con filtros opcionales
        sql_parts = [
            """
            SELECT 
                u.id,
                u.nombre,
                u.posicion,
                u.genero,
                TIMESTAMPDIFF(YEAR, u.fecha_nacimiento, CURDATE()) as edad,
                u.ubicacion_texto,
                u.latitud,
                u.longitud
            FROM usuarios u
            WHERE u.postulado = 1
            AND u.id != :organizador_id
            """
        ]

        params = {
            "organizador_id": organizador_id
        }

        if genero:
            sql_parts.append("AND u.genero = :genero")
            params["genero"] = genero.value

        if posicion:
            sql_parts.append("AND u.posicion = :posicion")
            params["posicion"] = posicion.value

        # Filtro por ubicación (búsqueda parcial, case & accent insensitive)
        if ubicacion_texto:
            ubicacion_normalizada = normalizar_texto(ubicacion_texto)
            sql_parts.append("AND LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(u.ubicacion_texto, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')) LIKE :ubicacion")
            params["ubicacion"] = f"%{ubicacion_normalizada}%"

        sql = text(" ".join(sql_parts))

        # Ejecutar query
        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, params).fetchall()

        # Calcular distancias y filtrar por distancia máxima
        jugadores_con_distancia = []
        for row in results:
            # Calcular distancia
            distancia = calcular_distancia(
                float(organizador.latitud),
                float(organizador.longitud),
                float(row.latitud),
                float(row.longitud),
            )

            # Filtrar por distancia máxima
            if distancia > distancia_maxima_km:
                continue

            # Agregar a resultados
            resultado = {
                "id": row.id,
                "nombre": row.nombre,
                "posicion": Posicion(row.posicion),
                "genero": Genero(row.genero),
                "edad": row.edad,
                "ubicacion_texto": row.ubicacion_texto,
                "distancia_km": round(distancia, 2),  # Redondear a 2 decimales
            }
            jugadores_con_distancia.append(resultado)

        # Ordenar por distancia (más cercanos primero)
        jugadores_con_distancia.sort(key=lambda x: x["distancia_km"])

        return jugadores_con_distancia