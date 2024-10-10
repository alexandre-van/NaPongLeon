FROM python:3.9-alpine

WORKDIR /app

# Copier seulement le fichier requirements.txt d'abord
COPY conf/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY ./src /app

ENV PYTHONPATH=/app

# Créer le répertoire pour les fichiers statiques collectés
RUN mkdir -p /app/staticfiles

# Copier explicitement les fichiers statiques
COPY ./src/agario/static /app/agario/static

# Collecter les fichiers statiques avec plus de verbosité
RUN python manage.py collectstatic --noinput -v 2

# Exposer le port pour Django
EXPOSE 8000

# Lancer le serveur Django
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "alt_game.asgi:application"]
