DC_FILE	= ./srcs/docker-compose.yml

start:
	@echo "Setting up host IP for OAuth..."
	chmod +x ./srcs/scripts/get_host_ip.sh
	./srcs/scripts/get_host_ip.sh
	@echo "Generating ssl certificates"
	chmod +x ./srcs/scripts/generate-certs.sh
	./srcs/scripts/generate-certs.sh
	@echo "Building and starting Docker containers and volumes"
	docker-compose -f $(DC_FILE) up -d --build --remove-orphans

stop:
	@echo "Shutting down Docker containers"
	docker-compose -f $(DC_FILE) stop --timeout=10

fclean:
	@echo "Stopping and removing specific containers..."
	@for container in postgres redis srcs-init_media-1 adminer nginx authentication hagarrio tournament frontend gamemanager pong ia; do \
		docker rm -f $$container 2>/dev/null || true; \
	done
	@echo "Removing specific Docker networks..."
	@for network in srcs_backend srcs_default srcs_frontend; do \
		docker network rm $$network 2>/dev/null || true; \
	done
	@echo "Removing specific Docker volumes..."
	@for volume in srcs_frontend_data srcs_redis_data srcs_postgres_data srcs_media_vol srcs_static_vol; do \
		docker volume rm $$volume 2>/dev/null || true; \
	done
	@echo "Removing specific Docker images..."
	@for image in alpine:latest redis:7.4 postgres:13 adminer:latest node:14-alpine python:3.9-alpine; do \
		docker rmi -f $$image 2>/dev/null || true; \
	done
	@docker rmi -f $(docker images --format "{{.Repository}}" | grep -E "requirements/|nginx" || echo "") 2>/dev/null || true
	@echo "Specified Docker resources cleaned up!"




remove_db:
	@echo "Removing volumes content"

re: stop start

.PHONY: start fclean re remove_db
