# Docker — teljes platform

Minden szolgáltatás egy `docker compose` paranccsal indul.

## Előfeltétel

- Docker Engine 24+
- Docker Compose v2

## Indítás

```bash
# A repo gyökeréből
cp infra/.env.example infra/.env
# Szerkeszd infra/.env — minimum: SECRETS_MASTER_KEY (32+ karakter élesben)

docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build
```

Első indításkor a `migrate` szolgáltatás lefuttatja az Alembic migrációkat, utána indulnak az app konténerek.

## Szolgáltatások

| Konténer | Port (host) | Leírás |
|----------|-------------|--------|
| `frontend-analytics` | 5174 | Beállítások, history, backtest |
| `frontend-realtime` | 5173 | Live WebSocket dashboard |
| `api` | 8000 | REST API |
| `realtime-ws` | 8001 | WebSocket gateway |
| `engine` | — | Stratégia futtató |
| `db-writer` | — | Kafka → PostgreSQL |
| `postgres` | 5432 | Adatbázis |
| `redpanda` | 19092 | Kafka kompatibilis broker |
| `redis` | 6379 | Config cache pub/sub |

## Böngésző URL-ek

- Analytics: http://localhost:5174
- Realtime: http://localhost:5173
- API docs: http://localhost:8000/docs

A frontend build során a `VITE_API_URL` és `VITE_WS_URL` a **host gépről** érhető el (localhost), nem a Docker belső hálózatról — így a böngésződ eléri az API-t.

Ha más gépről nyitod meg, állítsd az `infra/.env`-ben:

```env
VITE_API_URL=http://<szerver-ip>:8000
VITE_WS_URL=ws://<szerver-ip>:8001/realtime
```

majd: `docker compose -f infra/docker-compose.yml up -d --build frontend-realtime frontend-analytics`

## Hasznos parancsok

```bash
# Logok
docker compose -f infra/docker-compose.yml logs -f engine api db-writer

# Leállítás (adat megmarad)
docker compose -f infra/docker-compose.yml down

# Teljes törlés (PostgreSQL volume is)
docker compose -f infra/docker-compose.yml down -v

# Csak infrastruktúra (DB, Kafka, Redis) — fejlesztéshez helyi Pythonnal
docker compose -f infra/docker-compose.yml up -d postgres redpanda redis
```

## Bitunix API kulcsok

1. Nyisd meg http://localhost:5174
2. Add meg az API kulcsokat → mentés (titkosítva a PostgreSQL-ben)
3. Hozz létre stratégiát (Adaptive Ladder, dry_run mód ajánlott elsőre)
4. Az `engine` konténer a cache-ből olvassa a beállításokat

## Hibakeresés

- `migrate` konténer kilépett 0-val? → migráció OK
- Engine nem tradel: ellenőrizd `docker compose ... logs engine` — API kulcs és enabled stratégia kell
- Kafka hiba: várj, amíg a Redpanda healthy (`docker compose ps`)
