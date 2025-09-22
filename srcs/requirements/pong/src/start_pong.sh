#!/bin/sh
exec daphne -b 0.0.0.0 -p 8000 pong_project.asgi:application