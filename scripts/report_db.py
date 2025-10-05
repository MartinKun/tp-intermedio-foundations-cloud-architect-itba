import psycopg2
import os

print("==== Reporte de denuncias ====")

# Conexión DB
conn = psycopg2.connect(
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"],
    host=os.environ["PGHOST"],
    port=5432
)
cur = conn.cursor()

# 1. ¿Cómo ha evolucionado la cantidad de denuncias a lo largo del tiempo, desglosadas por año y por mes?
print("\n1. Evolución temporal de denuncias por año y mes:")
cur.execute("""
    SELECT 
        EXTRACT(YEAR FROM fecha_ingreso)::INT AS anio,
        EXTRACT(MONTH FROM fecha_ingreso)::INT AS mes,
        COUNT(*) AS cantidad_denuncias
    FROM denuncias
    GROUP BY anio, mes
    ORDER BY anio, mes;
""")
for anio, mes, cantidad in cur.fetchall():
    print(f"Año {anio}, Mes {mes:02d}: {cantidad} denuncias")

# 2. ¿Cuál es el subtema que registra la mayor cantidad de denuncias en toda la Argentina?
print("\n2. Subtema con mayor cantidad de denuncias a nivel nacional:")
cur.execute("""
    SELECT s.nombre AS subtema, COUNT(d.id) AS total_denuncias
    FROM denuncias d
    JOIN subtemas s ON d.subtema_id = s.id
    GROUP BY s.nombre
    ORDER BY total_denuncias DESC
    LIMIT 1;
""")
subtema, total = cur.fetchone()
print(f"Subtema: {subtema} - Total denuncias: {total}")

# 3. Para cada provincia, ¿cuál es el subtema que registra la mayor cantidad de denuncias y cuántas denuncias corresponden a ese subtema en esa provincia?
print("\n3. Subtema con mayor cantidad de denuncias por provincia:")
cur.execute("""
    SELECT DISTINCT ON (g.provincia)
           g.provincia,
           s.nombre AS subtema,
           COUNT(d.id) OVER (PARTITION BY g.provincia, s.id) AS cantidad_denuncias
    FROM denuncias d
    JOIN subtemas s ON d.subtema_id = s.id
    JOIN geo_entidades g ON d.geo_id = g.id
    ORDER BY g.provincia, cantidad_denuncias DESC;
""")
for provincia, subtema, cantidad in cur.fetchall():
    print(f"{provincia}: {subtema} ({cantidad} denuncias)")

# 4. ¿Cuál es la distribución de género de los denunciantes por provincia?
print("\n4. Distribución de género de los denunciantes por provincia:")
cur.execute("""
    SELECT
        g.provincia,
        dn.genero AS denunciante_genero,
        COUNT(*) AS cantidad,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY g.provincia), 2) AS porcentaje
    FROM denunciantes dn
    JOIN denuncias d ON dn.denuncia_id = d.id
    JOIN geo_entidades g ON d.geo_id = g.id
    GROUP BY g.provincia, dn.genero
    ORDER BY g.provincia, porcentaje DESC;
""")
for provincia, genero, cantidad, porcentaje in cur.fetchall():
    print(f"{provincia} - {genero}: {cantidad} ({porcentaje}%)")

# 5. Top subtemas con más derivaciones judicializadas por año
print("\n5. Top subtemas con más derivaciones judicializadas por año:")
cur.execute("""
    WITH judicializadas_por_subtema AS (
        SELECT
            EXTRACT(YEAR FROM d.fecha_ingreso)::INT AS anio,
            s.nombre AS subtema,
            COUNT(j.id) AS cantidad_judicializadas
        FROM derivaciones j
        JOIN denuncias d ON j.denuncia_id = d.id
        JOIN subtemas s ON d.subtema_id = s.id
        WHERE j.judicializa = TRUE
        GROUP BY EXTRACT(YEAR FROM d.fecha_ingreso), s.nombre
    ),
    ranked AS (
        SELECT
            anio,
            subtema,
            cantidad_judicializadas,
            ROW_NUMBER() OVER (
                PARTITION BY anio
                ORDER BY cantidad_judicializadas DESC
            ) AS rn
        FROM judicializadas_por_subtema
    )
    SELECT anio, subtema, cantidad_judicializadas
    FROM ranked
    WHERE rn <= 3
    ORDER BY anio, cantidad_judicializadas DESC;
""")
for anio, subtema, cantidad in cur.fetchall():
    print(f"Año {anio} - {subtema}: {cantidad} derivaciones judicializadas")

cur.close()
conn.close()
print("\n==== Fin del reporte ====")
