#!/bin/bash
# Script para crear las tablas en PostgreSQL usando Docker (Windows/Git Bash)

CONTAINER_NAME="postgres_tp"
SQL_LOCAL_PATH="$(pwd)/sql/create_tables.sql"
SQL_CONTAINER_PATH="/create_tables.sql"

# Copiar el SQL al contenedor
docker cp "$SQL_LOCAL_PATH" $CONTAINER_NAME:$SQL_CONTAINER_PATH

# Ejecutar el SQL dentro del contenedor
docker exec -i $CONTAINER_NAME bash -c "psql -U tp_user -d tp_db -f $SQL_CONTAINER_PATH"

echo "Tablas creadas (o ya existentes) en la base tp_db"