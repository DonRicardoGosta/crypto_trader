#!/bin/sh
set -e

export PYTHONPATH=/app/backend/src:${PYTHONPATH:-}
cd /app/infra/migrations
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://trading:trading@postgres:5432/trading}"

echo "Waiting for PostgreSQL before migrations..."
until python -c "
import socket, sys
s = socket.socket()
try:
    s.settimeout(2)
    s.connect(('postgres', 5432))
    sys.exit(0)
except Exception:
    sys.exit(1)
finally:
    s.close()
" 2>/dev/null; do
  sleep 1
done

echo "Running alembic upgrade head (${DATABASE_URL})"
alembic -c /app/infra/migrations/alembic.ini upgrade head
echo "Migrations complete."
