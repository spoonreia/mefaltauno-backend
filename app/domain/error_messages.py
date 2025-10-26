"""Mensajes de error centralizados"""

# ============================================
# ERRORES DE PARTIDOS
# ============================================
PARTIDO_NO_ENCONTRADO = "Partido no encontrado"
PARTIDO_COMPLETO = "El partido está completo"
PARTIDO_SIN_CUPO = "No hay cupos disponibles en el partido"
PARTIDO_ELIMINAR_TIEMPO = "No se puede eliminar un partido con menos de 24 horas de anticipación"
PARTIDO_CONTRASENA_INCORRECTA = "Contraseña incorrecta"
PARTIDO_CONTRASENA_REQUERIDA = "Este partido requiere contraseña"
PARTIDO_CONTRASENA_PRIVADO_REQUERIDA = "Los partidos privados requieren contraseña"
PARTIDO_YA_ORGANIZADOR = "Ya eres el organizador de este partido"
PARTIDO_YA_POSTULADO = "Ya tienes una postulación activa en este partido"

# ============================================
# ERRORES DE USUARIOS
# ============================================
USUARIO_NO_ENCONTRADO = "Usuario no encontrado"
JUGADOR_NO_ENCONTRADO = "Jugador no encontrado"
ORGANIZADOR_NO_ENCONTRADO = "Organizador no encontrado"
USUARIO_NO_POSTULADO = "El usuario no está postulado"

# ============================================
# ERRORES DE PARTICIPACIONES
# ============================================
PARTICIPACION_NO_ENCONTRADA = "Participación no encontrada"
PARTICIPACION_YA_EXISTE = "El jugador ya está participando en este partido"
PARTICIPACION_NO_ACTIVA = "No tienes una participación activa en este partido"
PARTICIPACION_SOLO_PENDIENTES_APROBAR = "Solo se pueden aprobar participaciones pendientes"
PARTICIPACION_SOLO_PENDIENTES_RECHAZAR = "Solo se pueden rechazar participaciones pendientes"
PARTICIPACION_SOLO_CONFIRMADAS_EXPULSAR = "Solo se pueden expulsar participaciones confirmadas"
PARTICIPACION_ORGANIZADOR_NO_SALE = "El organizador no puede salir de su propio partido"
PARTICIPACION_NO_GESTIONAR_PROPIA = "No puedes gestionar tu propia participación"

# ============================================
# ERRORES DE INVITACIONES
# ============================================
INVITACION_NO_ENCONTRADA = "Invitación no encontrada"
INVITACION_YA_PENDIENTE = "El jugador ya tiene una invitación pendiente"
INVITACION_YA_RESPONDIDA = "Esta invitación ya fue respondida"
INVITACION_NO_AUTORIZADA = "No puedes responder esta invitación"
INVITACION_NO_MISMO_JUGADOR = "No puedes invitarte a ti mismo"

# ============================================
# ERRORES DE PERMISOS
# ============================================
PERMISO_SOLO_ORGANIZADOR = "Solo el organizador puede realizar esta acción"
PERMISO_DENEGADO = "No tienes permisos para realizar esta acción"

# ============================================
# ERRORES DE VALIDACIÓN
# ============================================
CAPACIDAD_INVALIDA = "La capacidad no puede ser menor a los jugadores confirmados"
ACCION_INVALIDA = "Acción inválida. Debe ser: aprobar, rechazar o expulsar"

# ============================================
# MENSAJES DE ÉXITO
# ============================================
POSTULACION_ACTIVADA = "Te has postulado correctamente. Ahora aparecerás en las búsquedas de jugadores."
POSTULACION_DESACTIVADA = "Te has despostulado. Ya no aparecerás en las búsquedas de jugadores."
POSTULACION_ENVIADA = "Postulación enviada. Esperando aprobación del organizador"
INVITACION_ENVIADA = "Invitación enviada a {nombre}"
INVITACION_ACEPTADA = "Invitación aceptada. Te has unido al partido"
INVITACION_RECHAZADA = "Invitación rechazada"
PARTICIPACION_APROBADA = "{nombre} ha sido aprobado"
PARTICIPACION_RECHAZADA = "{nombre} ha sido rechazado"
PARTICIPACION_EXPULSADA = "{nombre} ha sido expulsado del partido"
PARTIDO_ELIMINADO = "Partido eliminado correctamente"
PARTIDO_SALIDA = "Has salido del partido (estabas {estado})"