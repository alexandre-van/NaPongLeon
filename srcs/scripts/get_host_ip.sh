#!/bin/bash

# Obtenir l'IP de l'hôte qui n'est pas localhost
HOST_IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}')

# Mettre à jour ou créer le fichier .env.web
ENV_FILE="./srcs/.env/.env.web"

#Vérifier si SITE_URL existe déjà dans le fichier
if grep -q "^SITE_URL=" "$ENV_FILE"; then
    # Remplacer la ligne existante
    sed -i "s|^SITE_URL=.*|SITE_URL=https://${HOST_IP}:8443|" "$ENV_FILE"
else
    # Ajouter la nouvelle variable
    echo "SITE_URL=https://${HOST_IP}:8443" >> "$ENV_FILE"
fi

echo "SITE_URL updated to https://${HOST_IP}:8443 in $ENV_FILE"



