#!/bin/sh
python manage.py makemigrations
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 game_manager_project.asgi:application