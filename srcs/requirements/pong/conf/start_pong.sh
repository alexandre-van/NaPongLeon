#!/bin/sh

#python src/manage.py makemigrations
#python src/manage.py migrate
nohup python src/manage.py runserver 0.0.0.0:8000 --noreload