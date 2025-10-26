"""Caso de uso: Crear Partido"""
from datetime import datetime, timezone, timedelta
from app.domain.models.partido import Partido
from app.domain.models.participacion import Participacion
from app.domain.enums.estado import EstadoPartido, EstadoParticipacion, TipoPartido
from app.infrastructure.repositories.partido_repository import PartidoRepository
from app.infrastructure.repositories.participacion_repository import ParticipacionRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.database.database_service import DatabaseConnection


class CrearPartidoUseCase:
    """Caso de uso para crear un partido"""

    def __init__(self, database_client: DatabaseConnection):
        self.database_client = database_client
        self.partido_repo = PartidoRepository(database_client)
        self.participacion_repo = ParticipacionRepository(database_client)
        self.usuario_repo = UsuarioRepository(database_client)

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

        # Validar que el organizador exista
        organizador = self.usuario_repo.obtener_por_id(organizador_id)
        if not organizador:
            raise ValueError("Organizador no encontrado")

        # Validar contraseña si es privado
        if tipo_partido == TipoPartido.PRIVADO and not contrasena:
            raise ValueError("Los partidos privados requieren contraseña")

        # Lógica de conversión de zona horaria
        fecha_hora_local = fecha_hora
        if fecha_hora.tzinfo:
            tz_argentina = timezone(timedelta(hours=-3))
            fecha_hora_local = fecha_hora.astimezone(tz_argentina)

        fecha_hora_naive = fecha_hora_local.replace(tzinfo=None)

        # Crear partido
        nuevo_partido = Partido(
            id=0,
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
        # El nombre del jugador se obtendrá automáticamente por el JOIN en el repositorio
        participacion_organizador = Participacion(
            id=0,
            partido_id=partido_creado.id,
            jugador_id=organizador_id,
            jugador_nombre=organizador.nombre,  # Lo usamos aquí pero no se guarda en DB
            estado=EstadoParticipacion.CONFIRMADO,
            fecha_postulacion=datetime.now(),
        )
        self.participacion_repo.crear(participacion_organizador)

        return partido_creado