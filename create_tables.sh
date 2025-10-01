#!/bin/bash
# Script para crear las tablas en la DB PostgreSQL
# ================================================
# Instrucciones:
# Antes de ejecutar este script, el usuario debe definir las variables de entorno:
#   export PGUSER=<tu_usuario>
#   export PGPASSWORD=<tu_contraseña>
#   export PGHOST=<host_de_postgres>        # normalmente localhost
#   export PGDATABASE=<nombre_de_la_base>
#
# Ejemplo:
#   export PGUSER=tp_user
#   export PGPASSWORD=tp_password
#   export PGHOST=localhost
#   export PGDATABASE=tp_db
#   ./create_tables.sh
#

# Verifica que las variables de entorno estén definidas
: "${PGUSER:?Por favor define PGUSER}"
: "${PGPASSWORD:?Por favor define PGPASSWORD}"
: "${PGHOST:?Por favor define PGHOST}"
: "${PGDATABASE:?Por favor define PGDATABASE}"

# Ejecuta el SQL de creación de tablas
psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -f create_tables.sql