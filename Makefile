.PHONY: docker-up docker-down docker-logs docker-build docker-ps

COMPOSE = docker compose -f infra/docker-compose.yml --env-file infra/.env

docker-up:
	cp -n infra/.env.example infra/.env 2>/dev/null || true
	$(COMPOSE) up -d --build

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f

docker-build:
	$(COMPOSE) build

docker-ps:
	$(COMPOSE) ps
