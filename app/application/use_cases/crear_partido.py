"""Caso de uso: Crear Partido"""
from datetime import datetime, timezone, timedelta
from app.domain.models.partido import Partido
from app.domain.models.participacion import Participacion
from app.domain.enums.estado import EstadoPartido, EstadoParticipacion, TipoPartido
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.in_memory_db import db_instance


class CrearPartidoUseCase:
    """Caso de uso para crear un partido"""

    def __init__(self):
        self.partido_repo = PartidoRepository(db_instance)

    def execute(
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
    ) -> Partido:
        """Ejecuta el caso de uso"""

        # Validar contraseña si es privado
        if tipo_partido == TipoPartido.PRIVADO and not contrasena:
            raise ValueError("Los partidos privados requieren contraseña")

        # ✅ 2. Lógica de conversión de zona horaria
        fecha_hora_local = fecha_hora
        if fecha_hora.tzinfo:
            # Define la zona horaria de Argentina (GMT-3)
            tz_argentina = timezone(timedelta(hours=-3))
            # Convierte la fecha UTC a la fecha local de Argentina
            fecha_hora_local = fecha_hora.astimezone(tz_argentina)

        # ✅ 3. Guarda la hora local correcta (16:00) pero sin info de timezone (naive)
        fecha_hora_naive = fecha_hora_local.replace(tzinfo=None)

        # Crear partido
        nuevo_partido = Partido(
            id=0,  # Se asignará en el repositorio
            titulo=titulo,
            dinero_por_persona=dinero_por_persona,
            descripcion=descripcion,
            fecha_hora=fecha_hora_naive,
            latitud=latitud,
            longitud=longitud,
            ubicacion_texto=ubicacion_texto,
            capacidad_maxima=capacidad_maxima,
            organizador_id=organizador_id,
            tipo_partido=tipo_partido,
            tipo_futbol=tipo_futbol,
            edad_minima=edad_minima,
            estado=EstadoPartido.PENDIENTE,
            contrasena=contrasena,
        )

        # Guardar en repositorio
        partido_creado = self.partido_repo.crear(nuevo_partido)

        # Agregar organizador como participante confirmado
        nueva_participacion_id = max([p.id for p in db_instance.participaciones_db], default=0) + 1
        organizador = next((u for u in db_instance.usuarios_db if u.id == organizador_id), None)
        
        participacion_organizador = Participacion(
            id=nueva_participacion_id,
            partido_id=partido_creado.id,
            jugador_id=organizador_id,
            jugador_nombre=organizador.nombre if organizador else "Desconocido",
            estado=EstadoParticipacion.CONFIRMADO,
            fecha_postulacion=datetime.now(),
        )
        db_instance.participaciones_db.append(participacion_organizador)

        return partido_creado