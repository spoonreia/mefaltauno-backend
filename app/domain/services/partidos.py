"""Servicio de dominio para Partidos - Todos los casos de uso"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.domain.repositories.partidos import PartidoRepositoryInterface
from app.domain.repositories.usuarios import UsuarioRepositoryInterface
from app.domain.repositories.participaciones import ParticipacionRepositoryInterface
from app.domain.repositories.invitaciones import InvitacionRepositoryInterface
from app.domain.schemas.partidos import TipoPartido, EstadoPartido, EstadoParticipacion, TipoFutbol
from app.domain.exceptions import (
    PartidoNoEncontradoException,
    PartidoCompletoException,
    ContrasenaIncorrectaException,
    PermisosDenegadosException,
    UsuarioNoEncontradoException,
)
from app.domain import error_messages as msg
from app.utils.date_utils import convertir_a_fecha_local, calcular_distancia
from app.utils.constants import HORAS_MINIMAS_ELIMINAR_PARTIDO


class PartidoService:
    """Servicio de dominio para gestionar partidos"""

    def __init__(
        self,
        partido_repo: PartidoRepositoryInterface,
        usuario_repo: UsuarioRepositoryInterface,
        participacion_repo: ParticipacionRepositoryInterface,
        invitacion_repo: InvitacionRepositoryInterface,
    ):
        self.partido_repo = partido_repo
        self.usuario_repo = usuario_repo
        self.participacion_repo = participacion_repo
        self.invitacion_repo = invitacion_repo

    # ============================================
    # CREAR PARTIDO
    # ============================================

    def crear(
        self,
        titulo: str,
        dinero_por_persona: int,
        descripcion: str,
        fecha_hora: datetime,
        latitud: float,
        longitud: float,
        ubicacion_texto: str,
        capacidad_maxima: int,
        tipo_partido: TipoPartido,
        tipo_futbol: str,
        edad_minima: int,
        organizador_id: int,
        contrasena: str = None,
    ) -> Dict[str, Any]:
        """Crea un nuevo partido"""

        # Validar que el organizador exista
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise UsuarioNoEncontradoException(msg.ORGANIZADOR_NO_ENCONTRADO)

        # Validar contraseña si es privado
        if tipo_partido == TipoPartido.PRIVADO and not contrasena:
            raise ValueError(msg.PARTIDO_CONTRASENA_PRIVADO_REQUERIDA)

        # Convertir fecha a local
        fecha_hora_naive = convertir_a_fecha_local(fecha_hora)

        # Crear partido
        partido_data = {
            'titulo': titulo,
            'dinero_por_persona': dinero_por_persona,
            'descripcion': descripcion,
            'fecha_hora': fecha_hora_naive,
            'latitud': latitud,
            'longitud': longitud,
            'ubicacion_texto': ubicacion_texto,
            'capacidad_maxima': capacidad_maxima,
            'organizador_id': organizador_id,
            'tipo_partido': tipo_partido.value,
            'tipo_futbol': tipo_futbol,
            'edad_minima': edad_minima,
            'estado': EstadoPartido.PENDIENTE.value,
            'contrasena': contrasena,
        }

        partido_creado = self.partido_repo.crear(partido_data)

        # Agregar organizador como participante confirmado
        participacion_data = {
            'partido_id': partido_creado['id'],
            'jugador_id': organizador_id,
            'estado': EstadoParticipacion.CONFIRMADO.value,
            'fecha_postulacion': datetime.now(),
        }
        self.participacion_repo.crear(participacion_data)

        return partido_creado

    # ============================================
    # EDITAR PARTIDO
    # ============================================

    def actualizar(
        self,
        partido_id: int,
        organizador_id: int,
        dinero_por_persona: Optional[int] = None,
        descripcion: Optional[str] = None,
        latitud: Optional[float] = None,
        longitud: Optional[float] = None,
        ubicacion_texto: Optional[str] = None,
        capacidad_maxima: Optional[int] = None,
        edad_minima: Optional[int] = None,
        contrasena: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Edita un partido existente"""

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # Validar permisos
        self._validar_organizador(partido, organizador_id)

        # Actualizar campos
        if dinero_por_persona is not None:
            partido['dinero_por_persona'] = dinero_por_persona

        if descripcion is not None:
            partido['descripcion'] = descripcion

        if latitud is not None:
            partido['latitud'] = latitud

        if longitud is not None:
            partido['longitud'] = longitud

        if ubicacion_texto is not None:
            partido['ubicacion_texto'] = ubicacion_texto

        if capacidad_maxima is not None:
            confirmados = self.participacion_repo.contar_por_estado(
                partido_id, EstadoParticipacion.CONFIRMADO.value
            )
            if capacidad_maxima < confirmados:
                raise ValueError(
                    msg.CAPACIDAD_INVALIDA + f" ({confirmados})"
                )
            partido['capacidad_maxima'] = capacidad_maxima

        if edad_minima is not None:
            partido['edad_minima'] = edad_minima

        # Gestionar privacidad
        if contrasena is not None:
            if contrasena == "":
                partido['tipo_partido'] = TipoPartido.PUBLICO.value
                partido['contrasena'] = None
            else:
                partido['tipo_partido'] = TipoPartido.PRIVADO.value
                partido['contrasena'] = contrasena

        # Actualizar
        return self.partido_repo.actualizar(partido_id, partido)

    # ============================================
    # ELIMINAR PARTIDO
    # ============================================

    def eliminar(self, partido_id: int, organizador_id: int) -> Dict[str, Any]:
        """Elimina un partido"""

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # Validar permisos
        self._validar_organizador(partido, organizador_id)

        # Validar tiempo
        if not self._puede_eliminar_partido(partido):
            raise ValueError(msg.PARTIDO_ELIMINAR_TIEMPO)

        # Eliminar participaciones e invitaciones
        self.participacion_repo.eliminar_por_partido(partido_id)
        self.invitacion_repo.eliminar_por_partido(partido_id)

        # Eliminar partido
        self.partido_repo.eliminar(partido_id)

        return {
            "mensaje": msg.PARTIDO_ELIMINADO,
            "partido_id": partido_id
        }

    # ============================================
    # BUSCAR PARTIDOS
    # ============================================

    def buscar(
        self,
        usuario_id: int,
        titulo: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        distancia_maxima_km: float = 5.0,
        tipo_futbol: Optional[TipoFutbol] = None,
        edad_minima: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Busca partidos disponibles"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Construir query SQL para buscar partidos
        from sqlalchemy import text

        sql_parts = [
            """
            SELECT DISTINCT
                p.id, p.titulo, p.dinero_por_persona, p.descripcion,
                p.fecha_hora, p.latitud, p.longitud, p.ubicacion_texto,
                p.capacidad_maxima, p.organizador_id, p.tipo_partido,
                p.tipo_futbol, p.edad_minima, p.estado,
                (SELECT COUNT(*) FROM participaciones part 
                 WHERE part.partido_id = p.id AND part.estado = :estado_confirmado) as jugadores_confirmados,
                (SELECT u.nombre FROM usuarios u WHERE u.id = p.organizador_id) as organizador_nombre
            FROM partidos p
            WHERE p.id NOT IN (
                SELECT pa.partido_id FROM participaciones pa 
                WHERE pa.jugador_id = :usuario_id 
                AND pa.estado IN (:estado_confirmado, :estado_pendiente)
            )
            AND p.fecha_hora >= NOW()
            """
        ]

        params = {
            "usuario_id": usuario_id,
            "estado_confirmado": EstadoParticipacion.CONFIRMADO.value,
            "estado_pendiente": EstadoParticipacion.PENDIENTE.value
        }

        # Agregar filtros opcionales
        if titulo:
            sql_parts.append("AND LOWER(p.titulo) LIKE :titulo")
            params["titulo"] = f"%{titulo.lower()}%"

        if fecha_desde:
            sql_parts.append("AND p.fecha_hora >= :fecha_desde")
            params["fecha_desde"] = fecha_desde

        if fecha_hasta:
            sql_parts.append("AND p.fecha_hora <= :fecha_hasta")
            params["fecha_hasta"] = fecha_hasta

        if tipo_futbol:
            sql_parts.append("AND p.tipo_futbol = :tipo_futbol")
            params["tipo_futbol"] = tipo_futbol.value

        if edad_minima is not None:
            sql_parts.append("AND p.edad_minima <= :edad_minima")
            params["edad_minima"] = edad_minima

        # Ejecutar query
        from app.infra.database.database import database_client
        sql = text(" ".join(sql_parts))

        with database_client.get_session("tt") as db:
            results = db.execute(sql, params).fetchall()

        # Filtrar por distancia y capacidad
        partidos_filtrados = []
        for row in results:
            # Verificar cupo
            if row.jugadores_confirmados >= row.capacidad_maxima:
                continue

            # Calcular distancia
            distancia = calcular_distancia(
                float(usuario['latitud']),
                float(usuario['longitud']),
                float(row.latitud),
                float(row.longitud),
            )

            if distancia > distancia_maxima_km:
                continue

            partidos_filtrados.append({
                "id": row.id,
                "titulo": row.titulo,
                "dinero_por_persona": row.dinero_por_persona,
                "descripcion": row.descripcion,
                "fecha_hora": row.fecha_hora,
                "latitud": row.latitud,
                "longitud": row.longitud,
                "ubicacion_texto": row.ubicacion_texto,
                "capacidad_maxima": row.capacidad_maxima,
                "jugadores_confirmados": row.jugadores_confirmados,
                "organizador_id": row.organizador_id,
                "organizador_nombre": row.organizador_nombre,
                "tipo_partido": row.tipo_partido,
                "tipo_futbol": row.tipo_futbol,
                "edad_minima": row.edad_minima,
                "estado": row.estado,
                "tiene_cupo": True,
                "distancia_km": distancia,
            })

        # Ordenar por distancia
        partidos_filtrados.sort(key=lambda x: x["distancia_km"])

        return partidos_filtrados

    # ============================================
    # VER DETALLE PARTIDO
    # ============================================

    def obtener_detalle(self, partido_id: int, usuario_id: int) -> Dict[str, Any]:
        """Obtiene el detalle completo de un partido"""

        # Verificar usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # Obtener participantes
        participaciones = self.participacion_repo.obtener_por_partido(partido_id)

        # Filtrar solo confirmados y pendientes
        participantes = [
            p for p in participaciones
            if p['estado'] in [
                EstadoParticipacion.CONFIRMADO.value,
                EstadoParticipacion.PENDIENTE.value
            ]
        ]

        # Ordenar: confirmados primero
        participantes.sort(
            key=lambda x: (
                x["estado"] != EstadoParticipacion.CONFIRMADO.value,
                x["fecha_postulacion"],
            )
        )

        # Contar participantes
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO.value
        )
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE.value
        )

        # Obtener organizador
        organizador = self.usuario_repo.obtener_por_id(partido['organizador_id'])

        return {
            **partido,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "organizador_nombre": organizador['nombre'] if organizador else "Desconocido",
            "tiene_cupo": confirmados < partido['capacidad_maxima'],
            "participantes": participantes,
        }

    # ============================================
    # POSTULARSE A PARTIDO
    # ============================================

    def postularse(
        self,
        partido_id: int,
        usuario_id: int,
        contrasena: str = None
    ) -> Dict[str, Any]:
        """Postularse a un partido"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # Validar que no sea el organizador
        if partido['organizador_id'] == usuario_id:
            raise ValueError(msg.PARTIDO_YA_ORGANIZADOR)

        # Validar que no esté ya postulado
        ya_postulado = self.participacion_repo.existe_participacion_activa(partido_id, usuario_id)
        if ya_postulado:
            raise ValueError(msg.PARTIDO_YA_POSTULADO)

        # Validar contraseña si es privado
        if partido['tipo_partido'] == TipoPartido.PRIVADO.value:
            if not contrasena:
                raise ValueError(msg.PARTIDO_CONTRASENA_REQUERIDA)
            if contrasena != partido['contrasena']:
                raise ContrasenaIncorrectaException(msg.PARTIDO_CONTRASENA_INCORRECTA)

        # Validar cupo
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO.value
        )
        if confirmados >= partido['capacidad_maxima']:
            raise PartidoCompletoException(msg.PARTIDO_COMPLETO)

        # Crear participación
        participacion_data = {
            'partido_id': partido_id,
            'jugador_id': usuario_id,
            'estado': EstadoParticipacion.PENDIENTE.value,
            'fecha_postulacion': datetime.now(),
        }
        self.participacion_repo.crear(participacion_data)

        # Contar pendientes
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE.value
        )

        return {
            "mensaje": msg.POSTULACION_ENVIADA,
            "partido_id": partido_id,
            "estado": "PENDIENTE",
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "capacidad_maxima": partido['capacidad_maxima'],
        }

    # ============================================
    # GESTIONAR PARTICIPACIÓN
    # ============================================

    def gestionar_participacion(
        self,
        partido_id: int,
        participacion_id: int,
        organizador_id: int,
        accion: str,
    ) -> Dict[str, Any]:
        """Gestiona una participación (aprobar/rechazar/expulsar)"""

        # Validar acción
        if accion not in ['aprobar', 'rechazar', 'expulsar']:
            raise ValueError(msg.ACCION_INVALIDA)

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # Validar permisos
        self._validar_organizador(partido, organizador_id)

        # Obtener participación
        participacion = self.participacion_repo.obtener_por_id(participacion_id)
        if not participacion or participacion['partido_id'] != partido_id:
            raise ValueError(msg.PARTICIPACION_NO_ENCONTRADA)

        # No puede gestionar su propia participación
        if participacion['jugador_id'] == organizador_id:
            raise ValueError(msg.PARTICIPACION_NO_GESTIONAR_PROPIA)

        # Ejecutar acción
        if accion == "aprobar":
            return self._aprobar_participacion(partido, participacion, participacion_id)
        elif accion == "rechazar":
            return self._rechazar_participacion(partido, participacion, participacion_id)
        elif accion == "expulsar":
            return self._expulsar_participacion(partido, participacion, participacion_id)

    def _aprobar_participacion(self, partido, participacion, participacion_id) -> Dict[str, Any]:
        """Aprueba una participación pendiente"""
        if participacion['estado'] != EstadoParticipacion.PENDIENTE.value:
            raise ValueError(msg.PARTICIPACION_SOLO_PENDIENTES_APROBAR)

        # Verificar cupo
        confirmados = self.participacion_repo.contar_por_estado(
            partido['id'], EstadoParticipacion.CONFIRMADO.value
        )
        if confirmados >= partido['capacidad_maxima']:
            raise PartidoCompletoException(msg.PARTIDO_COMPLETO)

        # Aprobar
        participacion['estado'] = EstadoParticipacion.CONFIRMADO.value
        self.participacion_repo.actualizar(participacion_id, participacion)

        mensaje = msg.PARTICIPACION_APROBADA.format(nombre=participacion['jugador_nombre'])
        return self._generar_respuesta_participacion(partido['id'], mensaje)

    def _rechazar_participacion(self, partido, participacion, participacion_id) -> Dict[str, Any]:
        """Rechaza una participación pendiente"""
        if participacion['estado'] != EstadoParticipacion.PENDIENTE.value:
            raise ValueError(msg.PARTICIPACION_SOLO_PENDIENTES_RECHAZAR)

        # Rechazar
        participacion['estado'] = EstadoParticipacion.RECHAZADO.value
        self.participacion_repo.actualizar(participacion_id, participacion)

        mensaje = msg.PARTICIPACION_RECHAZADA.format(nombre=participacion['jugador_nombre'])
        return self._generar_respuesta_participacion(partido['id'], mensaje)

    def _expulsar_participacion(self, partido, participacion, participacion_id) -> Dict[str, Any]:
        """Expulsa un participante confirmado"""
        if participacion['estado'] != EstadoParticipacion.CONFIRMADO.value:
            raise ValueError(msg.PARTICIPACION_SOLO_CONFIRMADAS_EXPULSAR)

        # Expulsar
        participacion['estado'] = EstadoParticipacion.CANCELADO.value
        self.participacion_repo.actualizar(participacion_id, participacion)

        mensaje = msg.PARTICIPACION_EXPULSADA.format(nombre=participacion['jugador_nombre'])
        return self._generar_respuesta_participacion(partido['id'], mensaje)

    def _generar_respuesta_participacion(self, partido_id: int, mensaje: str) -> Dict[str, Any]:
        """Genera la respuesta con conteos actualizados"""
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO.value
        )
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE.value
        )

        partido = self.partido_repo.obtener_por_id(partido_id)

        return {
            "mensaje": mensaje,
            "partido_id": partido_id,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
            "capacidad_maxima": partido['capacidad_maxima'],
        }

    # ============================================
    # SALIR DE PARTIDO
    # ============================================

    def salir(self, partido_id: int, usuario_id: int) -> Dict[str, Any]:
        """Salir de un partido"""

        # Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(msg.USUARIO_NO_ENCONTRADO)

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # El organizador no puede salir
        if partido['organizador_id'] == usuario_id:
            raise ValueError(msg.PARTICIPACION_ORGANIZADOR_NO_SALE)

        # Buscar participación activa
        participacion = self.participacion_repo.obtener_por_partido_y_jugador(partido_id, usuario_id)

        if not participacion or participacion['estado'] not in [
            EstadoParticipacion.PENDIENTE.value,
            EstadoParticipacion.CONFIRMADO.value
        ]:
            raise ValueError(msg.PARTICIPACION_NO_ACTIVA)

        # Guardar estado anterior
        estado_anterior = participacion['estado']

        # Cancelar participación
        participacion['estado'] = EstadoParticipacion.CANCELADO.value
        self.participacion_repo.actualizar(participacion['id'], participacion)

        # Contar participantes
        confirmados = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.CONFIRMADO.value
        )
        pendientes = self.participacion_repo.contar_por_estado(
            partido_id, EstadoParticipacion.PENDIENTE.value
        )

        return {
            "mensaje": msg.PARTIDO_SALIDA.format(estado=estado_anterior),
            "partido_id": partido_id,
            "jugadores_confirmados": confirmados,
            "jugadores_pendientes": pendientes,
        }

    # ============================================
    # INVITAR JUGADOR
    # ============================================

    def invitar_jugador(
        self,
        partido_id: int,
        jugador_id: int,
        organizador_id: int,
    ) -> Dict[str, Any]:
        """Invita un jugador a un partido"""

        # Verificar organizador
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise UsuarioNoEncontradoException(msg.ORGANIZADOR_NO_ENCONTRADO)

        # Verificar jugador
        jugador = self.usuario_repo.obtener_por_id(jugador_id)
        if not jugador:
            raise UsuarioNoEncontradoException(msg.JUGADOR_NO_ENCONTRADO)

        # Obtener partido
        partido = self.partido_repo.obtener_por_id(partido_id)
        if not partido:
            raise PartidoNoEncontradoException(msg.PARTIDO_NO_ENCONTRADO)

        # Validar permisos
        self._validar_organizador(partido, organizador_id)

        # No puede invitarse a sí mismo
        if jugador_id == organizador_id:
            raise ValueError(msg.INVITACION_NO_MISMO_JUGADOR)

        # Verificar que no esté ya participando
        ya_participa = self.participacion_repo.existe_participacion_activa(partido_id, jugador_id)
        if ya_participa:
            raise ValueError(msg.PARTICIPACION_YA_EXISTE)

        # Verificar que no tenga invitación pendiente
        ya_invitado = self.invitacion_repo.existe_invitacion_pendiente(partido_id, jugador_id)
        if ya_invitado:
            raise ValueError(msg.INVITACION_YA_PENDIENTE)

        # Crear invitación
        invitacion_data = {
            'partido_id': partido_id,
            'jugador_id': jugador_id,
            'estado': 'Pendiente',
            'fecha_invitacion': datetime.now(),
        }
        invitacion_creada = self.invitacion_repo.crear(invitacion_data)

        return {
            "mensaje": msg.INVITACION_ENVIADA.format(nombre=jugador['nombre']),
            "invitacion_id": invitacion_creada['id'],
        }

    # ============================================
    # MÉTODOS PRIVADOS
    # ============================================

    def _validar_organizador(self, partido: Dict[str, Any], usuario_id: int) -> None:
        """Valida que el usuario sea el organizador del partido"""
        if partido['organizador_id'] != usuario_id:
            raise PermisosDenegadosException(msg.PERMISO_SOLO_ORGANIZADOR)

    def _puede_eliminar_partido(self, partido: Dict[str, Any]) -> bool:
        """Verifica si un partido puede ser eliminado (más de 24h de anticipación)"""
        tiempo_restante = partido['fecha_hora'] - datetime.now()
        return tiempo_restante.total_seconds() >= HORAS_MINIMAS_ELIMINAR_PARTIDO * 3600