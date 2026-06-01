.PHONY: docker-up docker-down docker-logs docker-build docker-ps

docker-up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up -d --build

docker-down:
	docker compose down

docker-down-v:
	docker compose down -v

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build

docker-ps:
	docker compose ps
