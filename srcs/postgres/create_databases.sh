#!/bin/bash
set -e

# Lire les fichiers de secrets pour l'utilisateur et le mot de passe
POSTGRES_USER=$(cat $POSTGRES_USER_FILE)
POSTGRES_PASSWORD=$(cat $POSTGRES_PASSWORD_FILE)

export PGPASSWORD="$POSTGRES_PASSWORD"

# Vérifier si les bases de données sont définies
if [ -n "$POSTGRES_DB" ] && [ -n "$POSTGRES_DB_2" ]; then
    echo "Création des bases de données: $POSTGRES_DB, $POSTGRES_DB_2"
    
    for db in "$POSTGRES_DB" "$POSTGRES_DB_2"; do
        echo "Création de la base de données: $db"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOSQL
            CREATE DATABASE "$db";
EOSQL
    done

    echo "Bases de données créées avec succès"
else
    echo "Aucune base de données spécifiée"
fi
