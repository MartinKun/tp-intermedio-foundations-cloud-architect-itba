CREATE TABLE Provincias (
    provincia_id INT PRIMARY KEY,
    nombre VARCHAR(100),
    indec_id INT
);

CREATE TABLE Denuncias (
    denuncia_id BIGINT PRIMARY KEY,
    fecha_ingreso DATE NOT NULL,
    hora_ingreso TIME NOT NULL,
    situacion VARCHAR(100),
    origen VARCHAR(100),
    es_anonima BOOLEAN,
    tema VARCHAR(100),
    subtema VARCHAR(200),
    provincia_id INT,
    localidad VARCHAR(200),
    dependencia_alta VARCHAR(200),
    via_ingreso VARCHAR(200),
    provincia_indec_id INT,
    FOREIGN KEY (provincia_id) REFERENCES Provincias(provincia_id)
);

CREATE TABLE Derivaciones (
    derivacion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    denuncia_id BIGINT NOT NULL,
    institucion VARCHAR(200),
    fecha TIMESTAMP,
    judicializa BOOLEAN,
    FOREIGN KEY (denuncia_id) REFERENCES Denuncias(denuncia_id)
);

CREATE TABLE Denunciantes (
    denunciante_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    denuncia_id BIGINT NOT NULL,
    nacionalidad VARCHAR(100),
    provincia VARCHAR(100),
    localidad VARCHAR(100),
    tipo VARCHAR(100),
    como_conocio_linea VARCHAR(200),
    genero VARCHAR(100),
    edad_aparente INT,
    FOREIGN KEY (denuncia_id) REFERENCES Denuncias(denuncia_id)
);
