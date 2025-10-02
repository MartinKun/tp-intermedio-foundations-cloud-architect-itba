import requests
import psycopg2
import csv

# URL del nuevo CSV
url = "https://datos.jus.gob.ar/dataset/3b7de3f0-b62f-411e-9151-1a861fd3b170/resource/a78fc9f9-2608-4a65-bf98-eef5976caeba/download/oficina-rescate-orientaciones-referidos-202001-202508.csv"
csv_path = "/tmp/oficina_rescate.csv"

print("Descargando dataset...")
resp = requests.get(url)
if resp.status_code != 200:
    raise Exception(f"No se pudo descargar el CSV. Código HTTP: {resp.status_code}")

with open(csv_path, "wb") as f:
    f.write(resp.content)

# Conexión DB
conn = psycopg2.connect(
    dbname="tp_db",
    user="tp_user",
    password="tp_password",
    host="postgres_db",
    port=5432
)
cur = conn.cursor()

# Diccionario para provincias
prov_map = {}
prov_counter = 1

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=",")  # delimitador de este CSV

    for i, row in enumerate(reader):
        # Normalizar keys
        row = {k.strip().lower(): v for k, v in row.items()}

        # Ajustar nombres según columnas del CSV
        prov_name = row.get("provincia")
        prov_indec = row.get("provincia_indec_id")

        if not prov_name:
            print(f"⚠️ Fila sin provincia: {row}")
            continue

        if prov_name not in prov_map:
            cur.execute(
                "INSERT INTO Provincias (provincia_id, nombre, indec_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (prov_counter, prov_name, prov_indec if prov_indec else None)
            )
            prov_map[prov_name] = prov_counter
            prov_counter += 1

        provincia_id = prov_map[prov_name]

        # Denuncias
        denuncia_id = row.get("nro_registro_interno") or row.get("id_referencia")  # ajustar según CSV
        if not denuncia_id:
            print(f"⚠️ Fila sin ID de denuncia: {row}")
            continue

        cur.execute("""
            INSERT INTO Denuncias (
                denuncia_id, fecha_ingreso, hora_ingreso, situacion, origen,
                es_anonima, tema, subtema, provincia_id, localidad,
                dependencia_alta, via_ingreso, provincia_indec_id
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, (
            int(denuncia_id),
            row.get("fecha_ingreso"),
            row.get("hora_ingreso"),
            row.get("situacion"),
            row.get("origen"),
            True if row.get("es_anonima","").lower() in ["sí","si"] else False,
            row.get("tema"),
            row.get("subtema"),
            provincia_id,
            row.get("localidad"),
            row.get("dependencia_alta"),
            row.get("via_ingreso"),
            prov_indec if prov_indec else None
        ))

        # Derivaciones (hasta 3)
        for i in range(1, 4):
            inst = row.get(f"derivacion{i if i>1 else ''}_institucion")
            fecha = row.get(f"derivacion{i if i>1 else ''}_fecha")
            judi = row.get(f"derivacion{i if i>1 else ''}_judicializa")

            if inst:
                cur.execute("""
                    INSERT INTO Derivaciones (denuncia_id, institucion, fecha, judicializa)
                    VALUES (%s, %s, %s, %s)
                """, (
                    int(denuncia_id),
                    inst,
                    fecha if fecha else None,
                    True if judi and judi.lower() == "sí" else False
                ))

        # Denunciante
        cur.execute("""
            INSERT INTO Denunciantes (
                denuncia_id, nacionalidad, provincia, localidad, tipo,
                como_conocio_linea, genero, edad_aparente
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            int(denuncia_id),
            row.get("denunciante_nacionalidad"),
            row.get("denunciante_provincia"),
            row.get("denunciante_localidad"),
            row.get("denunciante_tipo"),
            row.get("denunciante_como_conocio_la_linea"),
            row.get("denunciante_genero"),
            int(row.get("denunciante_edad_aparente")) if row.get("denunciante_edad_aparente","0").isdigit() else None
        ))

conn.commit()
cur.close()
conn.close()
print("✅ Datos cargados correctamente")
