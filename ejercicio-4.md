# Ejercicio 4: Popular la base de datos

## Objetivo

Crear un script de Python que, una vez que el contenedor de PostgreSQL esté funcionando y se hayan ejecutado todas las
operaciones de DDL necesarias, cargue un dataset en la base de datos para dejarla lista para recibir consultas.

El script debe ejecutarse dentro de un contenedor Docker separado, sin incluir los datos crudos dentro del contenedor.
Para pasar los archivos CSV se puede usar un volumen (`-v`) o descargarlos desde Internet.

---

## Archivos principales

### `scripts/populate_db.py`

Script de Python que:

- Conecta a la base de datos usando variables de entorno (`PGUSER`, `PGPASSWORD`, `PGHOST`, `PGDATABASE`).
- Lee el CSV `oficina_rescate.csv` desde la carpeta `data`.
- Normaliza y valida los datos (IDs, fechas, booleanos, enteros).
- Inserta las filas en la tabla `denuncias_csv`.
- Muestra información en consola sobre el progreso: filas insertadas y filas saltadas.

#### Ejemplo de salida:

```bash
Usando CSV local: /app/../data/oficina_rescate.csv
Conectando a la base de datos en host: postgres_tp
Conexión establecida.
Columnas detectadas en CSV: ['nro_registro_interno', 'fecha_ingreso_consulta', ...]
Datos cargados correctamente. Total insertados: 757, saltados: 0
```

---

### `Dockerfile.populate`

Dockerfile para construir la imagen que ejecuta el script de carga:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
RUN pip install psycopg2-binary requests

# Copiar solo el script, no el CSV
COPY scripts/populate_db.py .

# Comando por defecto
CMD ["python", "populate_db.py"]
```

---

## Construcción de la imagen Docker

```bash
docker build -t populate-db -f Dockerfile.populate .
```

---

## Ejecución del script de carga

#### 1. Crear una red de Docker para que los contenedores se puedan comunicar:

```bash
docker network create tp_network
```

#### 2. Ejecutar el contenedor de carga, montando la carpeta data donde está el CSV y pasando las variables de entorno:

```bash
docker run --rm \
  --network tp_network \
  -e PGUSER=tp_user \
  -e PGPASSWORD=tp_password \
  -e PGHOST=postgres_tp \
  -e PGDATABASE=tp_db \
  -v D:/tp-intermedio-foundations-cloud-architect-itba/data:/data \
  populate-db
```

---

## Verificación

Para conectarse a PostgreSQL y realizar consultas de prueba, desde Git Bash en Windows:

```bash
winpty docker exec -it postgres_tp psql -U tp_user -d tp_db
```

Ejemplos de consultas:

```sql
-- Contar el total de registros
SELECT COUNT(*) FROM denuncias_csv;

-- Ver las primeras 5 filas
SELECT * FROM denuncias_csv LIMIT 5;
```

