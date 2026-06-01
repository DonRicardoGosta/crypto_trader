# Bitunix Futures Trading Platform

Monorepo for automated Bitunix futures trading with **unified execution** (live / dry-run / backtest), **Kafka → PostgreSQL** async persistence, and a **single web UI** (live WebSocket + settings/history).

## Structure

| Path | Description |
|------|-------------|
| [`requirements/`](requirements/) | Jira-style requirement docs (REQ-001 … REQ-007) |
| [`backend/`](backend/) | Python engine, API, Bitunix adapters |
| [`frontend/`](frontend/) | Unified React UI (port 5173) |
| [`infra/`](infra/) | Alembic migrations, Docker notes |

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
```

Open **http://localhost:5173** — Élő (WebSocket), Beállítások, Előzmények.

Local dev (backend + frontend separately):

```bash
cd backend && pip install -e ".[dev]"
export $(grep -v '^#' ../.env | xargs)
cd ../infra/migrations && alembic upgrade head
trading-api
trading-realtime-ws
trading-db-writer
trading-engine

cd frontend && npm install && npm run dev
```

## Configuration

- **Env only:** `DATABASE_URL`, `KAFKA_BOOTSTRAP`, `SECRETS_MASTER_KEY`
- **UI:** API keys, strategy params, risk limits → PostgreSQL via REST API

## Modes

All modes call the same `Strategy` + `RiskEngine`; only `ExecutionPort` / `MarketDataPort` adapters differ.

- **live** — real Bitunix orders
- **dry_run** — live market data, simulated fills (`SimulatedLedger`)
- **backtest** — historical kline replay, same ledger

## First strategy

`adaptive_ladder` — auto coin discovery, ladder positions, leverage bump on margin errors.

See [`docs/architecture.md`](docs/architecture.md).

## Docker (teljes stack)

```bash
cp .env.example .env
docker compose down -v
docker compose build --no-cache
docker compose down --remove-orphans   # régi frontend konténerek törlése
docker compose up -d
```

| Szolgáltatás | URL |
|--------------|-----|
| Web UI | http://localhost:5173 |
| API | http://localhost:8000 |
| WebSocket | ws://localhost:8001/realtime |
| PostgreSQL | localhost:5432 |
| Kafka (Redpanda) | localhost:19092 |

Leállítás: `docker compose down`

Logok: `docker compose logs -f engine api frontend`
