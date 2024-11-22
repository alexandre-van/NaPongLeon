FROM python:3.9-alpine

WORKDIR /app

# Copier seulement le fichier requirements.txt d'abord
COPY conf/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY ./src /app

ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=alt_game.settings

# Créer le répertoire pour les fichiers statiques collectés
RUN mkdir -p /app/staticfiles

# Copier explicitement les fichiers statiques
COPY ./src/agario/static /app/agario/static
COPY ./src/agario/static/fonts/helvetiker_regular.typeface.json /app/staticfiles/fonts/

# Collecter les fichiers statiques avec plus de verbosité
RUN pip install whitenoise

RUN python /app/manage.py collectstatic --noinput -v 2
RUN ls -R /app/staticfiles

# Exposer le port pour Django
EXPOSE 8000

# Lancer le serveur Django avec whitenoise
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "--root-path=/app", "alt_game.asgi:application"]
