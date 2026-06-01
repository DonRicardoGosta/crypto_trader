# Docker — teljes platform

Minden szolgáltatás egy `docker compose` paranccsal indul.

## Előfeltétel

- Docker Engine 24+
- Docker Compose v2

## Indítás

```bash
# A repo gyökeréből
cp .env.example .env
# Szerkeszd .env — minimum: SECRETS_MASTER_KEY (32+ karakter élesben)

docker compose up -d --build
```

Első indításkor a `migrate` szolgáltatás lefuttatja az Alembic migrációkat, utána indulnak az app konténerek.

## Szolgáltatások

| Konténer | Port (host) | Leírás |
|----------|-------------|--------|
| `frontend` | 5173 | Egyetlen UI: élő WS, beállítások, előzmények |
| `api` | 8000 | REST API |
| `realtime-ws` | 8001 | WebSocket gateway |
| `engine` | — | Stratégia futtató |
| `db-writer` | — | Kafka → PostgreSQL |
| `postgres` | 5432 | Adatbázis |
| `redpanda` | 19092 | Kafka kompatibilis broker |
| `redis` | 6380 (host) → 6379 | Config cache pub/sub |

## Böngésző

- **http://localhost:5173** — teljes felület (Élő / Beállítások / Előzmények)

## Hibaelhárítás

## Orphan konténerek / port 5173 foglalt

Ha a compose figyelmeztet régi `frontend-realtime` / `frontend-analytics` konténerekre, vagy a `frontend` nem indul (*port is already allocated*):

```bash
docker compose down --remove-orphans
docker rm -f crypto_trader-frontend-realtime-1 crypto_trader-frontend-analytics-1 2>/dev/null || true
docker compose up -d --build
```

Vagy: `make docker-clean && make docker-up`

Ha a 5173-at más folyamat használja (nem Docker):

```bash
# Linux
ss -tlnp | grep 5173
# Windows (PowerShell)
netstat -ano | findstr :5173
```

```bash
docker compose ps
docker compose logs -f migrate
docker compose logs -f frontend api engine
```

Teljes reset (adat törlése):

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```
