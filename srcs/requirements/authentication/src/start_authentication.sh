#!/bin/sh
python manage.py makemigrations --noinput
python manage.py migrate --noinput
exec daphne -b 0.0.0.0 -p 8000 authenticationProject.asgi:application