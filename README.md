# ITBA - Cloud Architect 2025 - TP Intermedio Foundations

Bienvenido al Trabajo Práctico Intermedio de la sección **Foundations** del Módulo 1 del curso en Cloud Architect 2025 del ITBA.  

En este trabajo se ponen en práctica los conocimientos adquiridos en:

- Bases de Datos Relacionales (PostgreSQL).
- BASH y Linux Commandline.
- Python 3.7+.
- Docker.

El objetivo fue resolver paso a paso los siguientes ejercicios, cada uno en un branch y con su Pull Request correspondiente.  

---

## Ejercicio 1: Elección de dataset y preguntas

El dataset elegido fue: **Lucha contra la trata de personas – denuncias Línea 145 (2020-01 a 2025-08)** 

Se plantearon al menos 4 preguntas de negocio que pueden responderse mediante consultas SQL.  

📄 Ver detalle en [`ejercicio-1.md`](./ejercicio-1.md).

---

## Ejercicio 2: Crear container de la DB

Se creó un archivo `docker-compose.yml` que levanta un contenedor con PostgreSQL 12.7, exponiendo el puerto **5432**.  

---

## Ejercicio 3: Script para creación de tablas

Se desarrolló el script de bash [`create_tables.sh`](./create_tables.sh) que ejecuta los scripts SQL de creación de tablas, llaves primarias y foráneas, sin insertar datos.  

---

## Ejercicio 4: Popular la base de datos

Se creó el script de Python [`populate_db.py`](./scripts/populate_db.py) que carga el dataset en las tablas ya creadas.  
Este script se corre dentro de un contenedor Docker mediante `docker run`.  

---

## Ejercicio 5: Consultas a la base de datos

Se creó el script [`report_db.py`](./scripts/report_db.py) que ejecuta consultas SQL de valor de negocio y muestra un reporte por pantalla.  

Las consultas implementadas son:

1. **Evolución temporal de denuncias**  
   ¿Cómo ha evolucionado la cantidad de denuncias por año entre 2020 y 2025?

2. **Distribución por provincia y tema**  
   ¿Qué provincias concentran la mayor cantidad de denuncias y cómo varía según el tema de la denuncia?

3. **Distribución por tipo de denunciante**  
   ¿Qué tipo de denunciante es más frecuente (persona, organización, etc.)?

4. **Promedio de edad de denunciantes por tema**  
   ¿Cuál es la edad promedio de los denunciantes según el tema de la denuncia?

---

## Ejercicio 6: Documentación y ejecución end-to-end

Se agregó este README consolidando los pasos de los ejercicios 1 a 5.  

Además, se creó el script [`run_end2end.sh`](./run_end2end.sh) que automatiza todo el flujo:  

1. Levanta el contenedor de PostgreSQL con Docker Compose.  
2. Ejecuta la creación de tablas (`create_tables.sh`).  
3. Carga los datos en la base (`populate_db.py` en Docker).  
4. Genera el reporte de consultas (`report_db.py` en Docker). 

---

### Preparación del entorno

Antes de ejecutar el flujo end-to-end, crear un archivo .env en la raíz del proyecto con las siguientes variables de conexión a la base de datos:

```bash
PGUSER=tp_user
PGPASSWORD=tp_password
PGHOST=postgres_tp
PGDATABASE=tp_db
```
Este archivo será utilizado por los contenedores Docker para conectarse a PostgreSQL.

---

### Ejecución end-to-end

```bash
./run_end2end.sh