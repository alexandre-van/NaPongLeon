#!/bin/sh
python manage.py makemigrations game_manager --noinput
python manage.py migrate --noinput
exec daphne -b 0.0.0.0 -p 8000 project.asgi:application