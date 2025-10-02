#!/bin/bash
set -e

echo "=== ITBA - TP Final Foundations ==="
echo "Ejecución end-to-end iniciada..."

# 1. Levantar el contenedor de PostgreSQL
echo ">>> Levantando contenedor PostgreSQL con docker-compose..."
docker-compose up -d

echo ">>> Esperando a que la base esté lista..."
sleep 10

# 2. Crear tablas
echo ">>> Creando tablas..."
bash create_tables.sh

# 3. Popular la base de datos
echo ">>> Populando la base de datos..."
docker build -t populate-db -f Dockerfile.populate .
docker run --rm \
  --network tp-intermedio-foundations-cloud-architect-itba_tp_network \
  --env-file .env \
  populate-db

# 4. Ejecutar consultas de negocio
echo ">>> Ejecutando consultas de negocio..."
docker build -t report-db -f Dockerfile.report .
docker run --rm \
  --network tp-intermedio-foundations-cloud-architect-itba_tp_network \
  --env-file .env \
  report-db

echo "=== Ejecución end-to-end finalizada ==="
