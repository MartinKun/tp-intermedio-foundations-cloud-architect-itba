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

# 1. Evolución temporal por año
print("\n1. Evolución temporal de denuncias por año:")
cur.execute("""
    SELECT EXTRACT(YEAR FROM fecha_ingreso)::INT AS anio, COUNT(*) 
    FROM denuncias_csv
    GROUP BY anio
    ORDER BY anio;
""")
for anio, total in cur.fetchall():
    print(f"Año {anio}: {total} denuncias")

# 2. Distribución por provincia y tema (top 10 combinaciones)
print("\n2. Distribución por provincia y tema (top 10 combinaciones):")
cur.execute("""
    SELECT provincia, tema, COUNT(*) AS total
    FROM denuncias_csv
    GROUP BY provincia, tema
    ORDER BY total DESC
    LIMIT 10;
""")
for provincia, tema, total in cur.fetchall():
    print(f"{provincia} - {tema}: {total}")

# 3. Distribución por tipo de denunciante
print("\n3. Distribución por tipo de denunciante:")
cur.execute("""
    SELECT denunciante_tipo, COUNT(*) AS total
    FROM denuncias_csv
    GROUP BY denunciante_tipo
    ORDER BY total DESC;
""")
for tipo, total in cur.fetchall():
    print(f"{tipo}: {total}")

# 4. Promedio de edad de los denunciantes por tema
print("\n4. Promedio de edad de los denunciantes por tema:")
cur.execute("""
    SELECT tema, ROUND(AVG(denunciante_edad_aparente))::INT AS edad_promedio
    FROM denuncias_csv
    WHERE denunciante_edad_aparente IS NOT NULL
    GROUP BY tema
    ORDER BY edad_promedio DESC;
""")
for tema, edad in cur.fetchall():
    print(f"{tema}: {edad} años")

cur.close()
conn.close()
print("\n==== Fin del reporte ====")
