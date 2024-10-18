DC_FILE	= ./srcs/docker-compose.yml

start:
	@echo "Building and starting Docker containers and volumes"
	docker-compose -f $(DC_FILE) up -d --build --remove-orphans

stop:
	@echo "Shutting down Docker containers"
	docker-compose -f $(DC_FILE) stop --timeout=4

fclean:
	@echo "Removing volumes and built containers"
	docker system prune -af
	docker volume ls -q | grep -v local | xargs -r docker volume rm

remove_db:
	@echo "Removing volumes content"

re: stop start

.PHONY: start fclean re remove_db
