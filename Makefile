DC_FILE	= ./srcs/docker-compose.yml

start:
	@echo "Generating ssl certificates"
	chmod +x ./srcs/scripts/generate-certs.sh
	./srcs/scripts/generate-certs.sh
	@echo "Building and starting Docker containers and volumes"
	docker-compose -f $(DC_FILE) up -d --build --remove-orphans

stop:
	@echo "Shutting down Docker containers"
	docker-compose -f $(DC_FILE) stop --timeout=10

fclean:
	@echo "Removing volumes and built containers"
	docker system prune -af
	docker volume ls -q | grep -v local | xargs -r docker volume rm
	rm ./srcs/ssl/*

remove_db:
	@echo "Removing volumes content"

re: stop start

.PHONY: start fclean re remove_db
