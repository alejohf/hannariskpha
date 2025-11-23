-- Script de creación de base de datos y tablas para "Ingeniería de Requisitos para Prevención y Gestión de Riesgos"
-- MySQL 8.0+
-- Usuario previsto: `root` con contraseña vacía (no se altera el usuario en este script)

CREATE DATABASE IF NOT EXISTS hana_riskpro CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE hana_riskpro;

-- TABLA: roles
CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE,
  descripcion TEXT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nombre_completo VARCHAR(255),
  email VARCHAR(255),
  rol_id INT NOT NULL,
  activo TINYINT(1) DEFAULT 1,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: sesiones (registro de login/logout)
CREATE TABLE IF NOT EXISTS sesiones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  token VARCHAR(512),
  inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fin TIMESTAMP NULL,
  ip VARCHAR(64),
  dispositivo VARCHAR(255),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: empresas
CREATE TABLE IF NOT EXISTS empresas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  ruc VARCHAR(50),
  direccion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: plantillas
CREATE TABLE IF NOT EXISTS plantillas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  contenido JSON,
  creado_por INT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: estudios
CREATE TABLE IF NOT EXISTS estudios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  empresa_id INT,
  ubicacion VARCHAR(255),
  objetivos TEXT,
  alcance TEXT,
  duracion VARCHAR(100),
  equipo_trabajo TEXT,
  documentos JSON,
  plantilla_id INT,
  creado_por INT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  actualizado_en TIMESTAMP NULL,
  activo TINYINT(1) DEFAULT 1,
  FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE SET NULL,
  FOREIGN KEY (plantilla_id) REFERENCES plantillas(id) ON DELETE SET NULL,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: subsistemas / areas
CREATE TABLE IF NOT EXISTS subsistemas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudio_id INT NOT NULL,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: nodos (equipos, líneas, sistemas)
CREATE TABLE IF NOT EXISTS nodos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudio_id INT NOT NULL,
  subsistema_id INT,
  nombre VARCHAR(255) NOT NULL,
  tipo VARCHAR(100),
  parametros JSON,
  dibujo VARCHAR(512),
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE,
  FOREIGN KEY (subsistema_id) REFERENCES subsistemas(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: parametros (opcional, detalle de parámetros por nodo)
CREATE TABLE IF NOT EXISTS parametros (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nodo_id INT NOT NULL,
  nombre VARCHAR(255) NOT NULL,
  valor VARCHAR(255),
  unidad VARCHAR(50),
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (nodo_id) REFERENCES nodos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: metodologias (HAZOP, What If, Checklist, Combinadas)
CREATE TABLE IF NOT EXISTS metodologias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO metodologias (codigo,nombre,descripcion) VALUES
('HAZOP','HAZOP','Análisis HAZOP'),
('WHATIF','WHAT IF','Metodología What If'),
('CHECK','CHECKLIST','Lista de verificación'),
('WIFCHK','WHATIF_CHECKLIST','Combinada');

-- TABLA: desviaciones (para HAZOP y DBD)
CREATE TABLE IF NOT EXISTS desviaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nodo_id INT NOT NULL,
  palabra_guia VARCHAR(100),
  parametro VARCHAR(100),
  descripcion TEXT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (nodo_id) REFERENCES nodos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: preguntas_whatif
CREATE TABLE IF NOT EXISTS preguntas_whatif (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subsistema_id INT,
  pregunta TEXT NOT NULL,
  descripcion TEXT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subsistema_id) REFERENCES subsistemas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: checklist_items
CREATE TABLE IF NOT EXISTS checklist_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subsistema_id INT,
  categoria VARCHAR(255),
  item TEXT NOT NULL,
  aplicable TINYINT(1) DEFAULT 1,
  cumplido TINYINT(1) DEFAULT 0,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subsistema_id) REFERENCES subsistemas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: causas (vinculadas a desviaciones o preguntas)
CREATE TABLE IF NOT EXISTS causas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  desviacion_id INT,
  pregunta_whatif_id INT,
  descripcion TEXT NOT NULL,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (desviacion_id) REFERENCES desviaciones(id) ON DELETE CASCADE,
  FOREIGN KEY (pregunta_whatif_id) REFERENCES preguntas_whatif(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: consecuencias
CREATE TABLE IF NOT EXISTS consecuencias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  desviacion_id INT,
  pregunta_whatif_id INT,
  descripcion TEXT NOT NULL,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (desviacion_id) REFERENCES desviaciones(id) ON DELETE CASCADE,
  FOREIGN KEY (pregunta_whatif_id) REFERENCES preguntas_whatif(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: salvaguardas (safeguards)
CREATE TABLE IF NOT EXISTS salvaguardas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudio_id INT,
  descripcion TEXT NOT NULL,
  tipo VARCHAR(100),
  eficacia VARCHAR(100),
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: recomendaciones
CREATE TABLE IF NOT EXISTS recomendaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudio_id INT NOT NULL,
  origen_tipo VARCHAR(50), -- 'desviacion','causa','consecuencia','checklist','whatif'
  origen_id INT,
  descripcion TEXT NOT NULL,
  responsable_id INT,
  estado ENUM('Pendiente','En Progreso','Completada','Cancelada') DEFAULT 'Pendiente',
  fecha_inicio_estimada DATE,
  fecha_fin_estimada DATE,
  fecha_inicio_real DATE,
  fecha_fin_real DATE,
  costo_estimado DECIMAL(12,2),
  prioridad INT DEFAULT 3,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE,
  FOREIGN KEY (responsable_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: historial_recomendaciones (registro de cambios)
CREATE TABLE IF NOT EXISTS historial_recomendaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  recomendacion_id INT NOT NULL,
  usuario_id INT,
  estado_anterior VARCHAR(64),
  estado_nuevo VARCHAR(64),
  comentario TEXT,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (recomendacion_id) REFERENCES recomendaciones(id) ON DELETE CASCADE,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: risk_matrices
CREATE TABLE IF NOT EXISTS risk_matrices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  creador_id INT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creador_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: risk_matrix_cells (celdas 1..25 con colores y códigos)
CREATE TABLE IF NOT EXISTS risk_matrix_cells (
  id INT AUTO_INCREMENT PRIMARY KEY,
  matriz_id INT NOT NULL,
  eje_x_codigo VARCHAR(10), -- por ejemplo A,B,C...
  eje_y_codigo VARCHAR(10), -- por ejemplo 1,2,3...
  codigo_riesgo INT NOT NULL,
  color VARCHAR(20),
  nivel VARCHAR(20), -- Alto, Medio, Bajo
  descripcion VARCHAR(255),
  FOREIGN KEY (matriz_id) REFERENCES risk_matrices(id) ON DELETE CASCADE,
  UNIQUE KEY unica_celda (matriz_id, eje_x_codigo, eje_y_codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: analisis_proceso (tabla genérica para entradas de análisis: desviaciones, whatif, checklist)
CREATE TABLE IF NOT EXISTS analisis_proceso (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudio_id INT NOT NULL,
  metodologia_id INT NOT NULL,
  nodo_id INT,
  desviacion_id INT,
  pregunta_whatif_id INT,
  checklist_item_id INT,
  descripcion TEXT,
  causas JSON,
  consecuencias JSON,
  salvaguardas JSON,
  recomendacion_id INT,
  severidad_codigo VARCHAR(10),
  frecuencia_codigo VARCHAR(10),
  risk_ranking INT,
  creado_por INT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE,
  FOREIGN KEY (metodologia_id) REFERENCES metodologias(id) ON DELETE RESTRICT,
  FOREIGN KEY (nodo_id) REFERENCES nodos(id) ON DELETE SET NULL,
  FOREIGN KEY (recomendacion_id) REFERENCES recomendaciones(id) ON DELETE SET NULL,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: adjuntos (archivos vinculados)
CREATE TABLE IF NOT EXISTS adjuntos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudio_id INT,
  analisis_id INT,
  nombre_archivo VARCHAR(512),
  ruta VARCHAR(1024),
  tipo_mime VARCHAR(255),
  tamano_bytes BIGINT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estudio_id) REFERENCES estudios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLA: auditoria (registros generales de acciones)
CREATE TABLE IF NOT EXISTS auditoria (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT,
  accion VARCHAR(255),
  objeto_tipo VARCHAR(100),
  objeto_id INT,
  detalle TEXT,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_estudio_metodologia ON analisis_proceso(estudio_id, metodologia_id);
CREATE INDEX IF NOT EXISTS idx_recomendacion_estudio ON recomendaciones(estudio_id);

-- PROCEDIMIENTOS ALMACENADOS (en español)
DELIMITER $$

-- Procedimiento: insertar un nuevo usuario
CREATE PROCEDURE sp_crear_usuario (
  IN p_username VARCHAR(150),
  IN p_password_hash VARCHAR(255),
  IN p_nombre_completo VARCHAR(255),
  IN p_email VARCHAR(255),
  IN p_rol_id INT
)
BEGIN
  INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol_id)
  VALUES (p_username, p_password_hash, p_nombre_completo, p_email, p_rol_id);
  SELECT LAST_INSERT_ID() AS nuevo_usuario_id;
END$$

-- Procedimiento: crear estudio
CREATE PROCEDURE sp_crear_estudio (
  IN p_nombre VARCHAR(255),
  IN p_empresa_id INT,
  IN p_ubicacion VARCHAR(255),
  IN p_objetivos TEXT,
  IN p_alcance TEXT,
  IN p_duracion VARCHAR(100),
  IN p_equipo_trabajo TEXT,
  IN p_documentos JSON,
  IN p_plantilla_id INT,
  IN p_creado_por INT
)
BEGIN
  INSERT INTO estudios (nombre, empresa_id, ubicacion, objetivos, alcance, duracion, equipo_trabajo, documentos, plantilla_id, creado_por)
  VALUES (p_nombre, p_empresa_id, p_ubicacion, p_objetivos, p_alcance, p_duracion, p_equipo_trabajo, p_documentos, p_plantilla_id, p_creado_por);
  SELECT LAST_INSERT_ID() AS nuevo_estudio_id;
END$$

-- Procedimiento: insertar recomendación
CREATE PROCEDURE sp_insertar_recomendacion (
  IN p_estudio_id INT,
  IN p_origen_tipo VARCHAR(50),
  IN p_origen_id INT,
  IN p_descripcion TEXT,
  IN p_responsable_id INT,
  IN p_costo DECIMAL(12,2),
  IN p_prioridad INT
)
BEGIN
  INSERT INTO recomendaciones (estudio_id, origen_tipo, origen_id, descripcion, responsable_id, costo_estimado, prioridad)
  VALUES (p_estudio_id, p_origen_tipo, p_origen_id, p_descripcion, p_responsable_id, p_costo, p_prioridad);
  SELECT LAST_INSERT_ID() AS nueva_recomendacion_id;
END$$

-- Procedimiento: actualizar estado de recomendación (y registrar historial)
CREATE PROCEDURE sp_actualizar_estado_recomendacion (
  IN p_recomendacion_id INT,
  IN p_nuevo_estado VARCHAR(64),
  IN p_usuario_id INT,
  IN p_comentario TEXT
)
BEGIN
  DECLARE v_estado_anterior VARCHAR(64);
  SELECT estado INTO v_estado_anterior FROM recomendaciones WHERE id = p_recomendacion_id;
  UPDATE recomendaciones SET estado = p_nuevo_estado WHERE id = p_recomendacion_id;
  INSERT INTO historial_recomendaciones (recomendacion_id, usuario_id, estado_anterior, estado_nuevo, comentario)
  VALUES (p_recomendacion_id, p_usuario_id, v_estado_anterior, p_nuevo_estado, p_comentario);
END$$

-- Procedimiento: obtener reporte resumido de un estudio (ejemplo simplificado)
CREATE PROCEDURE sp_obtener_reporte_estudio (
  IN p_estudio_id INT
)
BEGIN
  SELECT e.id AS estudio_id, e.nombre AS estudio_nombre, e.ubicacion, e.objetivos,
    (SELECT COUNT(*) FROM analisis_proceso ap WHERE ap.estudio_id = p_estudio_id) AS total_analisis,
    (SELECT COUNT(*) FROM recomendaciones r WHERE r.estudio_id = p_estudio_id) AS total_recomendaciones,
    (SELECT COUNT(*) FROM recomendaciones r WHERE r.estudio_id = p_estudio_id AND r.estado = 'Pendiente') AS pendientes
  FROM estudios e
  WHERE e.id = p_estudio_id;
END$$

-- Procedimiento: calcular risk ranking consultando la matriz (retorna codigo_riesgo)
CREATE PROCEDURE sp_calcular_rr (
  IN p_matriz_id INT,
  IN p_eje_x_codigo VARCHAR(10),
  IN p_eje_y_codigo VARCHAR(10)
)
BEGIN
  SELECT codigo_riesgo INTO @codigo FROM risk_matrix_cells
  WHERE matriz_id = p_matriz_id AND eje_x_codigo = p_eje_x_codigo AND eje_y_codigo = p_eje_y_codigo;
  SELECT @codigo AS codigo_riesgo;
END$$

DELIMITER ;

-- Datos iniciales: roles
INSERT IGNORE INTO roles (nombre, descripcion) VALUES
('Administrador','Usuario con todos los privilegios'),
('Colaborador','Usuario con permisos limitados');

-- Fin del script
