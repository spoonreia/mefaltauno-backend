"""Servicio de dominio para Usuarios"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import text

from app.domain.repositories.usuarios import UsuarioRepositoryInterface
from app.domain.exceptions import UsuarioNoEncontradoException
from app.domain.schemas.usuarios import Genero, Posicion
from app.domain import error_messages as msg
from app.utils.date_utils import calcular_distancia, normalizar_texto
from app.utils.constants import DIAS_CALENDARIO_FUTURO


class UsuarioService:
    """Servicio de dominio para gestionar usuarios"""

    def __init__(
        self,
        usuario_repo: UsuarioRepositoryInterface,
        database_client,
    ):
        self.usuario_repo = usuario_repo
        self.database_client = database_client

    # ============================================
    # OBTENER PERFIL
    # ============================================

    def obtener_perfil(self, usuario_id: int) -> Dict[str, Any]:
        """Obtiene el perfil completo de un usuario"""
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)
        return usuario

    # ============================================
    # ACTUALIZAR USUARIO
    # ============================================

    def actualizar(self, usuario_id: int, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un usuario"""
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Actualizar solo campos proporcionados
        for key, value in usuario_data.items():
            if value is not None:
                usuario[key] = value

        return self.usuario_repo.actualizar(usuario_id, usuario)

    # ============================================
    # ACTUALIZAR POSTULACIÓN
    # ============================================

    def actualizar_postulacion(self, usuario_id: int, activo: bool) -> Dict[str, Any]:
        """Actualiza el estado de postulación de un usuario"""
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Actualizar postulación
        self.usuario_repo.actualizar_postulacion(usuario_id, activo)

        # Mensaje según acción
        mensaje = msg.POSTULACION_ACTIVADA if activo else msg.POSTULACION_DESACTIVADA

        return {
            "mensaje": mensaje,
            "usuario_id": usuario_id,
            "postulado": activo,
        }

    # ============================================
    # BUSCAR JUGADORES DISPONIBLES
    # ============================================

    def buscar_jugadores_disponibles(
        self,
        organizador_id: int,
        genero: Optional[Genero] = None,
        posicion: Optional[Posicion] = None,
        ubicacion_texto: Optional[str] = None,
        distancia_maxima_km: float = 10.0,
    ) -> List[Dict[str, Any]]:
        """Busca jugadores postulados disponibles para invitar"""

        # Obtener organizador para calcular distancias
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise UsuarioNoEncontradoException(msg.ORGANIZADOR_NO_ENCONTRADO)

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

        params = {"organizador_id": organizador_id}

        if genero:
            sql_parts.append("AND u.genero = :genero")
            params["genero"] = genero.value

        if posicion:
            sql_parts.append("AND u.posicion = :posicion")
            params["posicion"] = posicion.value

        # Filtro por ubicación (búsqueda parcial, case & accent insensitive)
        if ubicacion_texto:
            ubicacion_normalizada = normalizar_texto(ubicacion_texto)
            sql_parts.append(
                "AND LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(u.ubicacion_texto, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')) LIKE :ubicacion"
            )
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
                float(organizador['latitud']),
                float(organizador['longitud']),
                float(row.latitud),
                float(row.longitud),
            )

            # Filtrar por distancia máxima
            if distancia > distancia_maxima_km:
                continue

            # Agregar a resultados
            jugadores_con_distancia.append({
                "id": row.id,
                "nombre": row.nombre,
                "posicion": row.posicion,
                "genero": row.genero,
                "edad": row.edad,
                "ubicacion_texto": row.ubicacion_texto,
                "distancia_km": distancia,
            })

        # Ordenar por distancia (más cercanos primero)
        jugadores_con_distancia.sort(key=lambda x: x["distancia_km"])

        return jugadores_con_distancia

    # ============================================
    # OBTENER CALENDARIO
    # ============================================

    def obtener_calendario(
        self,
        usuario_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene el calendario de partidos de un usuario"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Fechas por defecto
        ahora = datetime.now()
        if not fecha_desde:
            fecha_desde = ahora
        else:
            if fecha_desde.tzinfo is not None:
                fecha_desde = fecha_desde.replace(tzinfo=None)

        if not fecha_hasta:
            fecha_hasta = ahora + timedelta(days=DIAS_CALENDARIO_FUTURO)
        else:
            if fecha_hasta.tzinfo is not None:
                fecha_hasta = fecha_hasta.replace(tzinfo=None)

        # Query SQL para obtener partidos del usuario
        sql = text(
            """
            SELECT 
                p.id,
                p.titulo,
                p.fecha_hora,
                p.ubicacion_texto,
                p.organizador_id,
                p.capacidad_maxima,
                p.tipo_partido,
                (p.organizador_id = :usuario_id) as es_organizador,
                (SELECT COUNT(*) 
                 FROM participaciones part 
                 WHERE part.partido_id = p.id 
                 AND part.estado = 'Confirmado') as jugadores_confirmados
            FROM partidos p
            INNER JOIN participaciones pa ON p.id = pa.partido_id
            WHERE pa.jugador_id = :usuario_id
            AND pa.estado = 'Confirmado'
            AND p.fecha_hora >= :fecha_desde
            AND p.fecha_hora <= :fecha_hasta
            AND p.fecha_hora >= :ahora
            ORDER BY p.fecha_hora ASC
            """
        )

        with self.database_client.get_session("tt") as db:
            results = db.execute(sql, {
                "usuario_id": usuario_id,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "ahora": ahora
            }).fetchall()

        # Convertir resultados
        return [
            {
                "id": row.id,
                "titulo": row.titulo,
                "fecha_hora": row.fecha_hora,
                "ubicacion_texto": row.ubicacion_texto,
                "es_organizador": bool(row.es_organizador),
                "jugadores_confirmados": row.jugadores_confirmados,
                "capacidad_maxima": row.capacidad_maxima,
                "tipo_partido": row.tipo_partido,
            }
            for row in results
        ]