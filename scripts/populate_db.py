import psycopg2
import csv
from datetime import datetime
import os
import requests
import unicodedata

# --- CONFIG ---
DOWNLOAD_URL = "https://datos.jus.gob.ar/dataset/1326870f-4eb7-42df-882e-8a022cf953b5/resource/c78aeb4e-666f-401e-8724-c4b32d9a9d3a/download/oficina-rescate-denuncias-202001-202508.csv"
csv_path = "/tmp/oficina_rescate.csv"

# --- Funciones ---
def normalize_text(val):
    """Quita acentos y reemplaza vacíos por 'Sin Especificar'"""
    if not val or val.strip() == "":
        return "Sin Especificar"
    val = val.strip()
    val = unicodedata.normalize('NFKD', val).encode('ASCII', 'ignore').decode('ASCII')
    return val

def parse_datetime(val):
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except:
        return None

def parse_bool(val):
    return str(val).lower() in ["si", "sí", "yes", "true"]

def parse_int(val):
    try:
        return int(val)
    except:
        return None

# --- Descargar CSV ---
print("Descargando CSV...")
resp = requests.get(DOWNLOAD_URL)
resp.raise_for_status()
with open(csv_path, "wb") as f:
    f.write(resp.content)
print(f"CSV descargado ({os.path.getsize(csv_path) / (1024*1024):.2f} MB)")

# --- Conexión DB ---
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
temas_cache = {}
subtemas_cache = {}
geo_cache = {}

insertados_denuncias = 0
saltados = 0

with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=",")
    for idx, row in enumerate(reader):
        row = {k.strip(): v.strip() for k, v in row.items()}

        # -----------------------------
        # Temas
        # -----------------------------
        tema_nombre = normalize_text(row.get("tema"))
        if tema_nombre not in temas_cache:
            cur.execute("INSERT INTO temas (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING RETURNING id", (tema_nombre,))
            res = cur.fetchone()
            tema_id = res[0] if res else None
            if not tema_id:
                cur.execute("SELECT id FROM temas WHERE nombre=%s", (tema_nombre,))
                tema_id = cur.fetchone()[0]
            temas_cache[tema_nombre] = tema_id
        tema_id = temas_cache[tema_nombre]

        # -----------------------------
        # Subtemas
        # -----------------------------
        subtema_nombre = normalize_text(row.get("subtema"))
        subtema_key = (tema_id, subtema_nombre)
        if subtema_key not in subtemas_cache:
            cur.execute("""
                INSERT INTO subtemas (tema_id, nombre) VALUES (%s,%s)
                ON CONFLICT (tema_id,nombre) DO NOTHING RETURNING id
            """, (tema_id, subtema_nombre))
            res = cur.fetchone()
            if res:
                subtema_id = res[0]
            else:
                cur.execute("SELECT id FROM subtemas WHERE tema_id=%s AND nombre=%s", (tema_id, subtema_nombre))
                subtema_id = cur.fetchone()[0]
            subtemas_cache[subtema_key] = subtema_id
        subtema_id = subtemas_cache[subtema_key]

        # -----------------------------
        # Geo entidades
        # -----------------------------
        provincia = normalize_text(row.get("provincia"))
        localidad = normalize_text(row.get("localidad"))
        geo_key = (provincia, localidad)
        if geo_key not in geo_cache:
            provincia_indec_id = parse_int(row.get("provincia_indec_id"))
            cur.execute("""
                INSERT INTO geo_entidades (provincia, localidad, provincia_indec_id)
                VALUES (%s,%s,%s)
                RETURNING id
            """, (provincia, localidad, provincia_indec_id))
            geo_id = cur.fetchone()[0]
            geo_cache[geo_key] = geo_id
        geo_id = geo_cache[geo_key]

        # -----------------------------
        # Denuncias
        # -----------------------------
        nro_id = parse_int(row.get("nro_registro_interno"))
        if not nro_id:
            saltados += 1
            continue

        fecha_ingreso = parse_datetime(row.get("fecha_ingreso")) or None
        hora_ingreso = None
        situacion = normalize_text(row.get("situacion"))
        origen = normalize_text(row.get("origen"))
        es_anonima = parse_bool(row.get("es_anonima"))
        dependencia_alta = normalize_text(row.get("dependencia_alta"))
        via_ingreso = normalize_text(row.get("via_ingreso"))

        try:
            cur.execute("""
                INSERT INTO denuncias (
                    nro_registro_interno, fecha_ingreso, hora_ingreso, situacion, origen,
                    es_anonima, tema_id, subtema_id, dependencia_alta, via_ingreso, geo_id
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (nro_registro_interno) DO NOTHING
                RETURNING id
            """, (
                nro_id, fecha_ingreso, hora_ingreso, situacion, origen,
                es_anonima, tema_id, subtema_id, dependencia_alta, via_ingreso, geo_id
            ))
            res = cur.fetchone()
            if not res:
                cur.execute("SELECT id FROM denuncias WHERE nro_registro_interno=%s", (nro_id,))
                denuncia_id = cur.fetchone()[0]
            else:
                denuncia_id = res[0]
            insertados_denuncias += 1
        except Exception as e:
            print(f"Fila {idx} saltada (denuncia): {e}")
            saltados += 1
            continue

        # -----------------------------
        # Denunciantes
        # -----------------------------
        cur.execute("""
            INSERT INTO denunciantes (
                denuncia_id, nacionalidad, tipo, como_conocio_la_linea, genero, edad_aparente
            ) VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            denuncia_id,
            normalize_text(row.get("denunciante_nacionalidad")),
            normalize_text(row.get("denunciante_tipo")),
            normalize_text(row.get("denunciante_como_conocio_la_linea")),
            normalize_text(row.get("denunciante_genero")),
            parse_int(row.get("denunciante_edad_aparente"))
        ))

        # -----------------------------
        # Derivaciones
        # -----------------------------
        for n in range(1, 4):
            institucion = normalize_text(row.get(f"derivacion{'' if n==1 else n}_institucion"))
            fecha = parse_datetime(row.get(f"derivacion{'' if n==1 else n}_fecha"))
            judicializa = parse_bool(row.get(f"derivacion{'' if n==1 else n}_judicializa"))
            if institucion != "Sin Especificar" or fecha or judicializa:
                cur.execute("""
                    INSERT INTO derivaciones (denuncia_id, numero, institucion, fecha, judicializa)
                    VALUES (%s,%s,%s,%s,%s)
                """, (denuncia_id, n, institucion, fecha, judicializa))

conn.commit()
cur.close()
conn.close()
print(f"Datos cargados. Denuncias insertadas: {insertados_denuncias}, filas saltadas: {saltados}")
