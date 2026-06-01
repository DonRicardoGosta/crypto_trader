.PHONY: docker-up docker-down docker-down-v docker-clean docker-logs docker-build docker-ps

docker-up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose down --remove-orphans 2>/dev/null || true
	-docker rm -f crypto_trader-frontend-realtime-1 crypto_trader-frontend-analytics-1 2>/dev/null || true
	docker compose up -d --build --remove-orphans

docker-down:
	docker compose down --remove-orphans

docker-down-v:
	docker compose down -v --remove-orphans

# Régi frontend-realtime / frontend-analytics konténerek + port ütközés
docker-clean:
	docker compose down --remove-orphans
	-docker rm -f crypto_trader-frontend-realtime-1 crypto_trader-frontend-analytics-1 2>/dev/null || true

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build

docker-ps:
	docker compose ps
