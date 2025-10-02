# Ejercicio 3: Crear tablas PostgreSQL

## Objetivo
Crear un script de Bash que ejecute uno o varios scripts SQL para crear las tablas de la base de datos en el container PostgreSQL levantado en el ejercicio anterior. Se deben crear únicamente las tablas, claves primarias, claves foráneas y otras operaciones de DDL, sin insertar datos.

---

## 1. Levantar el container de PostgreSQL
Levantar el container:
```bash
docker-compose up -d
```
Verificar que está corriendo:
```bash
docker ps
```
## 2. Definir variables de entorno
En Git Bash o Linux/macOS:
```bash
export PGUSER=tp_user
export PGPASSWORD=tp_password
export PGHOST=localhost
export PGDATABASE=tp_db
```
En PowerShell:
```bash
$env:PGUSER="tp_user"
$env:PGPASSWORD="tp_password"
$env:PGHOST="localhost"
$env:PGDATABASE="tp_db"
```
## 3. Ejecutar script de creación de tablas
Asegúrate de que create_tables.sh tiene permisos de ejecución y está en la raíz del proyecto:
```bash
chmod +x create_tables.sh
./create_tables.sh
```
## 4. Verificar las tablas
Entrar al container:
```bash
winpty docker exec -it postgres_tp bash
psql -U tp_user -d tp_db
```

Listar tablas:
```bash
\dt
```