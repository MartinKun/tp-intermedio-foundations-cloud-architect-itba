# Ejercicio 5: Consultas a la base de datos

## Objetivo
Crear un script de Python que realice al menos 5 consultas SQL que aporten valor al negocio y muestre un reporte con los resultados.  
El script debe ejecutarse mediante Docker, al igual que en el ejercicio 4.

---

## 1. Preparar el script de reporting

1. Crear el archivo `scripts/report_db.py` con las consultas deseadas. Por ejemplo, este script incluye:

   1. Evolución temporal de denuncias por año.
   2. Distribución de denuncias por provincia y tema (top 10 combinaciones).
   3. Distribución por tipo de denunciante.
   4. Promedio de edad de los denunciantes por tema.

2. Verificar que las consultas funcionan correctamente desde `psql` antes de incluirlas en el script.

---

## 2. Dockerfile para el reporte

Archivo `Dockerfile.report`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install psycopg2-binary

# Copiar el script de reporting
COPY scripts/report_db.py .

CMD ["python", "report_db.py"]
```

---

## 3. Construir la imagen Docker

Desde la raíz del proyecto:

```bash
docker build -t report-db -f Dockerfile.report .
```

---

## 4. Ejecutar el reporte con Docker

Usando la misma red de Docker que la base de datos (tp_network) y las variables de entorno de conexión:

```bash
docker build -t report-db -f Dockerfile.report .
```

El script imprimirá en consola un reporte con los resultados de las consultas.



