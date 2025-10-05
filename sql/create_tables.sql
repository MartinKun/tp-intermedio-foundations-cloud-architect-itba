-- -----------------------------
-- Tabla de temas
-- -----------------------------
CREATE TABLE temas (
    id BIGSERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

-- -----------------------------
-- Tabla de subtemas
-- -----------------------------
CREATE TABLE subtemas (
    id BIGSERIAL PRIMARY KEY,
    tema_id BIGINT NOT NULL REFERENCES temas(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    UNIQUE (tema_id, nombre)
);

-- -----------------------------
-- Tabla de entidades geográficas (provincia + localidad)
-- -----------------------------
CREATE TABLE geo_entidades (
    id BIGSERIAL PRIMARY KEY,
    provincia TEXT NOT NULL,
    localidad TEXT,
    provincia_indec_id INT
);

-- -----------------------------
-- Tabla de denuncias
-- -----------------------------
CREATE TABLE denuncias (
    id BIGSERIAL PRIMARY KEY,
    nro_registro_interno BIGINT UNIQUE NOT NULL,
    fecha_ingreso DATE NOT NULL,
    hora_ingreso TIME,
    situacion TEXT NOT NULL,
    origen TEXT NOT NULL,
    es_anonima BOOLEAN NOT NULL,
    tema_id BIGINT NOT NULL REFERENCES temas(id) ON DELETE RESTRICT,
    subtema_id BIGINT NOT NULL REFERENCES subtemas(id) ON DELETE RESTRICT,
    dependencia_alta TEXT NOT NULL,
    via_ingreso TEXT,
    geo_id BIGINT REFERENCES geo_entidades(id) ON DELETE SET NULL
);

-- -----------------------------
-- Tabla de denunciantes
-- -----------------------------
CREATE TABLE denunciantes (
    id BIGSERIAL PRIMARY KEY,
    denuncia_id BIGINT NOT NULL REFERENCES denuncias(id) ON DELETE CASCADE,
    nacionalidad TEXT,
    tipo TEXT,
    como_conocio_la_linea TEXT,
    genero TEXT,
    edad_aparente INT
);

-- -----------------------------
-- Tabla de derivaciones
-- -----------------------------
CREATE TABLE derivaciones (
    id BIGSERIAL PRIMARY KEY,
    denuncia_id BIGINT NOT NULL REFERENCES denuncias(id) ON DELETE CASCADE,
    numero INT NOT NULL, -- 1, 2 o 3
    institucion TEXT,
    fecha TIMESTAMP,
    judicializa BOOLEAN
);