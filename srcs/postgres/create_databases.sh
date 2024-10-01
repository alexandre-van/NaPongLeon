#!/bin/bash
set -e

if [ -n "$POSTGRES_DB_2" ]; then
    echo "Création des bases de données: $POSTGRES_DB, $POSTGRES_DB_2"
    psql --username="$POSTGRES_USER" -d postgres <<EOSQL
        CREATE DATABASE "$POSTGRES_DB_2";
EOSQL
fi