#!/bin/sh
set -e
cd /app/infra/migrations
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://trading:trading@postgres:5432/trading}"
alembic upgrade head
echo "Migrations complete."
