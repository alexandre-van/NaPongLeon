#!/bin/sh
exec daphne -b 0.0.0.0 -p 8000 tournament_project.asgi:application