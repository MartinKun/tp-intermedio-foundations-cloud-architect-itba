# Ejercicio 4: Popular la base de datos

## Objetivo
Crear un script de Python que, una vez que el container de la base de datos se encuentre corriendo y se hayan ejecutado todas las operaciones de DDL necesarias, poblar la base de datos con el dataset elegido.

---

## 1. Construir el contenedor

```bash
docker build -t db-populate -f Dockerfile.populate .
```

## 2. Ejecutar el contenedor
Asegurarse de que la base de datos PostgreSQL esté corriendo en el mismo docker network. Por ejemplo:

```bash
docker network ls
```

y usar el network que corresponda, por ejemplo tp-intermedio-foundations-cloud-architect-itba_default.

Luego ejecutar:

```bash
docker run --rm \
  --network tp-intermedio-foundations-cloud-architect-itba_default \
  db-populate:latest
```

El script descargará el CSV directamente desde Internet, lo procesará y cargará los datos en la base.

---

### Validación rápida
Conectarse a la base y revisar algunas filas:
```bash
docker exec -it postgres_tp psql -U tp_user -d tp_db
```
