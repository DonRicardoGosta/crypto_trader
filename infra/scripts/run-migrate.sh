#!/bin/sh
set -eu

export PYTHONPATH=/app/backend/src
cd /app/infra/migrations
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://trading:trading@postgres:5432/trading}"

echo "Waiting for PostgreSQL..."
until python -c "import socket,sys;s=socket.socket();s.settimeout(2);s.connect(('postgres',5432));s.close()"; do
  sleep 2
done

echo "Running alembic upgrade head"
alembic -c /app/infra/migrations/alembic.ini upgrade head
echo "Migrations complete."
