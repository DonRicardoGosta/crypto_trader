# Trading Platform Backend

Bitunix futures trading engine with unified execution ports, Kafka async persistence, and FastAPI.

## Services

| Command | Description |
|---------|-------------|
| `trading-api` | Config + history REST (port 8000) |
| `trading-engine` | Strategy runner |
| `trading-db-writer` | Kafka → PostgreSQL consumer |
| `trading-realtime-ws` | Live WebSocket gateway (port 8001) |

## Setup

```bash
cd backend
pip install -e ".[dev]"
```

Env (minimal): `DATABASE_URL`, `KAFKA_BOOTSTRAP`, `SECRETS_MASTER_KEY`.
