FROM python:3.9-alpine

WORKDIR /app

# Copier seulement le fichier requirements.txt d'abord
COPY conf/requirements.txt ./

RUN pip install --upgrade pip
# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install redis

# Copier le reste du code source
COPY . .

# Exposer le port pour Django
EXPOSE 8000

# Lancer le serveur Django
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "src.alt_game.asgi:application"]
