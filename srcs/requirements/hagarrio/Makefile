DOCKER_COMPOSE = docker compose
SERVICE_NAME = alt_game
HOSTNAME = $(shell hostname -s)

all: up

up:
	@ if [ ! -f .env ]; then \
		echo "Please create a .env file"; \
		exit 1; \
	fi
	@ if [ -z "$$(grep -E '^HOST_NAME=' .env)" ]; then \
		echo "HOST_NAME=$(HOSTNAME)" >> .env; \
	else \
		if [ "$$(uname)" = "Darwin" ]; then \
			sed -i '' -E 's/^HOST_NAME=.*/HOST_NAME=$(HOSTNAME)/' .env; \
		else \
			sed -i 's/^HOST_NAME=.*/HOST_NAME=$(HOSTNAME)/' .env; \
		fi \
	fi
	$(DOCKER_COMPOSE) up --build -d

stop:
	$(DOCKER_COMPOSE) down

fclean:
	docker system prune -af

.PHONY: all up stop fclean