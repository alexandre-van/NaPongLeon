FROM python:3.9-alpine

WORKDIR /app

# Copier seulement le fichier requirements.txt d'abord
COPY conf/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=alt_game.settings
ENV CORS_ALLOW_ALL_ORIGINS=True
ENV CORS_ALLOW_CREDENTIALS=True

# Exposer le port pour Django
EXPOSE 8000

# Lancer le serveur Django avec daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "alt_game.asgi:application"]
