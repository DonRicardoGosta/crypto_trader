# Bitunix Futures Trading Platform

Monorepo for automated Bitunix futures trading with **unified execution** (live / dry-run / backtest), **Kafka → PostgreSQL** async persistence, and **split frontends** (realtime WebSocket vs analytics DB).

## Structure

| Path | Description |
|------|-------------|
| [`requirements/`](requirements/) | Jira-style requirement docs (REQ-001 … REQ-007) |
| [`backend/`](backend/) | Python engine, API, Bitunix adapters |
| [`frontend-realtime/`](frontend-realtime/) | WebSocket dashboard (port 5173) |
| [`frontend-analytics/`](frontend-analytics/) | Settings, history, backtests (port 5174) |
| [`infra/`](infra/) | Docker Compose (Postgres, Redpanda, Redis), Alembic |

## Quick start

```bash
cd infra && docker compose up -d
cd ../backend && pip install -e ".[dev]"
cp ../.env.example ../.env
export $(grep -v '^#' ../.env | xargs)
cd ../infra/migrations && alembic upgrade head
```

Services (separate terminals):

```bash
trading-api           # http://localhost:8000
trading-realtime-ws   # ws://localhost:8001/realtime
trading-db-writer
trading-engine
```

Frontends:

```bash
cd frontend-realtime && npm install && npm run dev
cd frontend-analytics && npm install && npm run dev
```

## Configuration

- **Env only:** `DATABASE_URL`, `KAFKA_BOOTSTRAP`, `SECRETS_MASTER_KEY`
- **Frontend/UI:** API keys, strategy params, risk limits → PostgreSQL via analytics API

## Modes

All modes call the same `Strategy` + `RiskEngine`; only `ExecutionPort` / `MarketDataPort` adapters differ.

- **live** — real Bitunix orders
- **dry_run** — live market data, simulated fills (`SimulatedLedger`)
- **backtest** — historical kline replay, same ledger

## First strategy

`adaptive_ladder` — auto coin discovery, ladder positions, leverage bump on margin errors.

See [`docs/architecture.md`](docs/architecture.md).


## Docker (teljes stack)

A repo gyökeréből (a `.env` automatikusan betöltődik):

```bash
cp .env.example .env
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

| Szolgáltatás | URL |
|--------------|-----|
| Analytics UI | http://localhost:5174 |
| Realtime UI | http://localhost:5173 |
| API | http://localhost:8000 |
| WebSocket | ws://localhost:8001/realtime |
| PostgreSQL | localhost:5432 |
| Kafka (Redpanda) | localhost:19092 |

Leállítás: `docker compose -f infra/docker-compose.yml down`

Logok: `docker compose -f infra/docker-compose.yml logs -f engine api`
