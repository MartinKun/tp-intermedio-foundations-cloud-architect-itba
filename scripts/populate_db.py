import psycopg2
import csv
from datetime import datetime
import os
import requests

# --- CONFIG ---
DOWNLOAD_URL = "https://datos.jus.gob.ar/dataset/3b7de3f0-b62f-411e-9151-1a861fd3b170/resource/a78fc9f9-2608-4a65-bf98-eef5976caeba/download/oficina-rescate-orientaciones-referidos-202001-202508.csv"
csv_path = "/tmp/oficina_rescate.csv"

# Descargar CSV
print("Descargando CSV desde Internet...")
resp = requests.get(DOWNLOAD_URL)
if resp.status_code != 200:
    raise Exception(f"No se pudo descargar el CSV. Código HTTP: {resp.status_code}")
with open(csv_path, "wb") as f:
    f.write(resp.content)

print(f"Usando CSV: {csv_path}")

# --- Conexión DB ---
print("Conectando a la base de datos en host:", os.environ.get("PGHOST"))
conn = psycopg2.connect(
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"],
    host=os.environ["PGHOST"],
    port=5432
)
cur = conn.cursor()
print("Conexión establecida.")

# --- Insertar datos ---
insertados = 0
saltados = 0

with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=",")
    print("Columnas detectadas en CSV:", reader.fieldnames)

    for idx, row in enumerate(reader):
        row = {k.strip(): v.strip() for k, v in row.items()}

        # Validar ID
        nro_id = row.get("nro_registro_interno")
        if not nro_id or not nro_id.isdigit():
            print(f"Fila {idx} saltada: nro_registro_interno inválido -> {nro_id}")
            saltados += 1
            continue
        nro_id = int(nro_id)

        # Fechas
        fecha_ingreso = row.get("fecha_ingreso_consulta") or None
        hora_ingreso = None

        def parse_datetime(val):
            if not val:
                return None
            try:
                return datetime.fromisoformat(val)
            except:
                return None

        derivacion_fecha = parse_datetime(row.get("derivacion_fecha"))
        derivacion2_fecha = parse_datetime(row.get("derivacion2_fecha"))
        derivacion3_fecha = parse_datetime(row.get("derivacion3_fecha"))

        # Booleanos
        es_anonima = row.get("es_anonima", "").lower() in ["sí", "si", "yes", "true"]
        derivacion_judicializa = row.get("derivacion_judicializa", "").lower() in ["sí", "si", "yes", "true"]
        derivacion2_judicializa = row.get("derivacion2_judicializa", "").lower() in ["sí", "si", "yes", "true"]
        derivacion3_judicializa = row.get("derivacion3_judicializa", "").lower() in ["sí", "si", "yes", "true"]

        # Edad
        edad = row.get("edad_aparente")
        edad = int(edad) if edad and edad.isdigit() else None

        # Insert
        try:
            cur.execute("""
                INSERT INTO denuncias_csv (
                    fecha_ingreso, hora_ingreso, nro_registro_interno, situacion, origen,
                    es_anonima, tema, subtema, provincia, localidad, dependencia_alta, via_ingreso,
                    derivacion_institucion, derivacion_fecha, derivacion_judicializa,
                    derivacion2_institucion, derivacion2_fecha, derivacion2_judicializa,
                    derivacion3_institucion, derivacion3_fecha, derivacion3_judicializa,
                    denunciante_nacionalidad, denunciante_provincia, denunciante_localidad,
                    denunciante_tipo, denunciante_como_conocio_la_linea, denunciante_genero,
                    denunciante_edad_aparente, provincia_indec_id
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (nro_registro_interno) DO NOTHING
            """, (
                fecha_ingreso, hora_ingreso, nro_id, row.get("situacion"), row.get("origen"),
                es_anonima, row.get("tema"), row.get("subtema"), row.get("provincia"), row.get("localidad"),
                row.get("dependencia_alta"), row.get("via_ingreso"),
                row.get("derivacion_institucion"), derivacion_fecha, derivacion_judicializa,
                row.get("derivacion2_institucion"), derivacion2_fecha, derivacion2_judicializa,
                row.get("derivacion3_institucion"), derivacion3_fecha, derivacion3_judicializa,
                row.get("nacionalidad"), row.get("provincia"), row.get("localidad"),
                row.get("referido_tipo"), None, row.get("genero"),
                edad, int(row.get("provincia_indec_id")) if row.get("provincia_indec_id") else None
            ))
            insertados += 1
        except Exception as e:
            print(f"Fila {idx} saltada: error -> {e}")
            saltados += 1

conn.commit()
cur.close()
conn.close()
print(f"Datos cargados correctamente. Total insertados: {insertados}, saltados: {saltados}")
