"""Caso de uso: Buscar Partidos"""
from typing import List, Optional
from datetime import datetime
from app.domain.models.partido import Partido
from app.domain.enums.estado import TipoFutbol, EstadoParticipacion
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.repositories.in_memory_db import db_instance
from app.infrastructure.utils.calculadora_distancia import calcular_distancia


class BuscarPartidosUseCase:
    """Caso de uso para buscar partidos"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)
        self.usuario_repo = UsuarioRepository(db_instance)

    def execute(
        self,
        usuario_id: int,
        titulo: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        distancia_maxima_km: float = 5.0,
        tipo_futbol: Optional[TipoFutbol] = None,
        edad_minima: Optional[int] = None,
    ) -> List[dict]:
        """Ejecuta el caso de uso"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Obtener partidos donde el usuario ya participa
        partidos_usuario = {
            p.partido_id 
            for p in db_instance.participaciones_db 
            if p.jugador_id == usuario_id 
            and p.estado in [EstadoParticipacion.CONFIRMADO, EstadoParticipacion.PENDIENTE]
        }

        # Buscar partidos
        partidos = self.partido_repo.buscar(
            titulo=titulo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            tipo_futbol=tipo_futbol,
            edad_minima=edad_minima,
        )

        # Filtrar y enriquecer resultados
        resultados = []
        for partido in partidos:
            # Excluir partidos donde ya participa
            if partido.id in partidos_usuario:
                continue

            # Calcular distancia
            distancia = calcular_distancia(
                usuario.latitud,
                usuario.longitud,
                partido.latitud,
                partido.longitud,
            )

            # Filtrar por distancia
            if distancia > distancia_maxima_km:
                continue

            # Contar confirmados
            confirmados = len([
                p for p in db_instance.participaciones_db
                if p.partido_id == partido.id 
                and p.estado == EstadoParticipacion.CONFIRMADO
            ])

            # Solo partidos con cupo
            if confirmados >= partido.capacidad_maxima:
                continue

            if edad_minima is not None:
                print(partido.edad_minima, edad_minima)
                if partido.edad_minima > edad_minima:
                    continue

            # Obtener organizador
            organizador = self.usuario_repo.obtener_por_id(partido.organizador_id)

            # Crear resultado
            resultado = {
                "id": partido.id,
                "titulo": partido.titulo,
                "dinero_por_persona": partido.dinero_por_persona,
                "descripcion": partido.descripcion,
                "fecha_hora": partido.fecha_hora,
                "latitud": partido.latitud,
                "longitud": partido.longitud,
                "ubicacion_texto": partido.ubicacion_texto,
                "capacidad_maxima": partido.capacidad_maxima,
                "jugadores_confirmados": confirmados,
                "organizador_id": partido.organizador_id,
                "organizador_nombre": organizador.nombre if organizador else "Desconocido",
                "tipo_partido": partido.tipo_partido,
                "tipo_futbol": partido.tipo_futbol,
                "edad_minima": partido.edad_minima,
                "estado": partido.estado,
                "tiene_cupo": True,
                "distancia_km": distancia,
            }
            resultados.append(resultado)

        # Ordenar por distancia
        resultados.sort(key=lambda x: x["distancia_km"])

        return resultados