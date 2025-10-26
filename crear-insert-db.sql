-- Eliminar base de datos si existe
DROP DATABASE IF EXISTS yojuego;

-- Crear base de datos
CREATE DATABASE yojuego
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE yojuego;

-- ============================================
-- TABLA: usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    latitud DECIMAL(10, 7) NOT NULL CHECK (latitud >= -90 AND latitud <= 90),
    longitud DECIMAL(10, 7) NOT NULL CHECK (longitud >= -180 AND longitud <= 180),
    ubicacion_texto VARCHAR(255) NOT NULL,
    descripcion TEXT,
    genero ENUM('Masculino', 'Femenino', 'Otro') NOT NULL,
    posicion ENUM('Arquero', 'Defensa', 'Mediocampista', 'Delantero') NOT NULL,
    postulado BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_usuarios_postulado (postulado),
    INDEX idx_usuarios_genero (genero),
    INDEX idx_usuarios_posicion (posicion),
    INDEX idx_usuarios_ubicacion (ubicacion_texto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: partidos
-- ============================================
CREATE TABLE IF NOT EXISTS partidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    dinero_por_persona INT NOT NULL CHECK (dinero_por_persona >= 0),
    descripcion TEXT,
    fecha_hora DATETIME NOT NULL,
    latitud DECIMAL(10, 7) NOT NULL CHECK (latitud >= -90 AND latitud <= 90),
    longitud DECIMAL(10, 7) NOT NULL CHECK (longitud >= -180 AND longitud <= 180),
    ubicacion_texto VARCHAR(255) NOT NULL,
    capacidad_maxima INT NOT NULL CHECK (capacidad_maxima >= 2 AND capacidad_maxima <= 22),
    organizador_id INT NOT NULL,
    tipo_partido ENUM('Publico', 'Privado') NOT NULL,
    tipo_futbol ENUM('Futbol 5', 'Futbol 7', 'Futbol 11') NOT NULL,
    edad_minima INT NOT NULL CHECK (edad_minima >= 16 AND edad_minima <= 99),
    estado ENUM('Pendiente', 'Confirmado', 'Cancelado', 'Finalizado') NOT NULL DEFAULT 'Pendiente',
    contrasena VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_partido_organizador FOREIGN KEY (organizador_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_partidos_fecha_hora (fecha_hora),
    INDEX idx_partidos_organizador (organizador_id),
    INDEX idx_partidos_tipo_futbol (tipo_futbol),
    INDEX idx_partidos_estado (estado),
    INDEX idx_partidos_tipo_partido (tipo_partido)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: participaciones
-- ============================================
CREATE TABLE IF NOT EXISTS participaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partido_id INT NOT NULL,
    jugador_id INT NOT NULL,
    estado ENUM('Pendiente', 'Confirmado', 'Rechazado', 'Cancelado') NOT NULL DEFAULT 'Pendiente',
    fecha_postulacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_participacion_partido FOREIGN KEY (partido_id) 
        REFERENCES partidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_participacion_jugador FOREIGN KEY (jugador_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_participacion_partido_jugador UNIQUE (partido_id, jugador_id),
    INDEX idx_participaciones_partido (partido_id),
    INDEX idx_participaciones_jugador (jugador_id),
    INDEX idx_participaciones_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: invitaciones
-- ============================================
CREATE TABLE IF NOT EXISTS invitaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partido_id INT NOT NULL,
    jugador_id INT NOT NULL,
    estado ENUM('Pendiente', 'Aceptada', 'Rechazada') NOT NULL DEFAULT 'Pendiente',
    fecha_invitacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_invitacion_partido FOREIGN KEY (partido_id) 
        REFERENCES partidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_invitacion_jugador FOREIGN KEY (jugador_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_invitacion_partido_jugador UNIQUE (partido_id, jugador_id),
    INDEX idx_invitaciones_partido (partido_id),
    INDEX idx_invitaciones_jugador (jugador_id),
    INDEX idx_invitaciones_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLA: calificaciones
-- ============================================
CREATE TABLE IF NOT EXISTS calificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partido_id INT NOT NULL,
    calificador_id INT NOT NULL,
    calificado_id INT NOT NULL,
    puntuacion INT NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_calificacion_partido FOREIGN KEY (partido_id) 
        REFERENCES partidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_calificacion_calificador FOREIGN KEY (calificador_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_calificacion_calificado FOREIGN KEY (calificado_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_calificacion_partido_calificador_calificado 
        UNIQUE (partido_id, calificador_id, calificado_id),
    CHECK (calificador_id != calificado_id),
    INDEX idx_calificaciones_partido (partido_id),
    INDEX idx_calificaciones_calificador (calificador_id),
    INDEX idx_calificaciones_calificado (calificado_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================
-- DATOS DE EJEMPLO
-- ============================================

INSERT INTO usuarios (nombre, fecha_nacimiento, latitud, longitud, ubicacion_texto, descripcion, genero, posicion, postulado) VALUES
('Juan Pérez', '1996-05-15', -34.7050, -58.5648, 'Morón, Buenos Aires', 'Jugador amateur, me gusta el fútbol desde chico', 'Masculino', 'Mediocampista', false),
('María González', '1999-08-22', -34.6764, -58.5640, 'Castelar, Buenos Aires', 'Delantero, juego hace 10 años', 'Femenino', 'Delantero', true),
('Carlos Rodríguez', '1992-03-10', -34.6590, -58.6227, 'Ituzaingó, Buenos Aires', 'Arquero experimentado', 'Masculino', 'Arquero', true),
('Laura Martínez', '2001-11-30', -34.7100, -58.5700, 'Morón, Buenos Aires', 'Defensora rápida', 'Femenino', 'Defensa', true),
('Alex Torres', '1997-07-18', -34.6800, -58.5800, 'Castelar, Buenos Aires', 'Juego en cualquier posición', 'Otro', 'Mediocampista', false);

-- Ejemplo de partido
INSERT INTO partidos (titulo, dinero_por_persona, descripcion, fecha_hora, latitud, longitud, ubicacion_texto, capacidad_maxima, organizador_id, tipo_partido, tipo_futbol, edad_minima, estado)
VALUES ('Futbol 5 - Sábado tarde', 5000, 'Partido tranquilo para pasar el rato', DATE_ADD(NOW(), INTERVAL 2 DAY), -34.7050, -58.5648, 'Complejo La Cancha, Morón', 10, 1, 'Publico', 'Futbol 5', 18, 'Pendiente');

-- Participación del organizador
INSERT INTO participaciones (partido_id, jugador_id, estado)
VALUES (1, 1, 'Confirmado');

-- ============================================
-- VERIFICACIÓN
-- ============================================

SHOW TABLES;

SELECT 
	id, 
	nombre, 
	posicion,
	TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) as edad, 
	ubicacion_texto,
	descripcion,
	genero
FROM usuarios
where id = :idUsuario;

