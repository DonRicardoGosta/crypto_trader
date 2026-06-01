#!/bin/sh
set -e

wait_for_postgres() {
  echo "Waiting for PostgreSQL..."
  until python -c "
import socket
import sys
host = '${POSTGRES_HOST:-postgres}'
port = int('${POSTGRES_PORT:-5432}')
s = socket.socket()
try:
    s.settimeout(2)
    s.connect((host, port))
    sys.exit(0)
except Exception:
    sys.exit(1)
finally:
    s.close()
" 2>/dev/null; do
    sleep 1
  done
  echo "PostgreSQL is up."
}

if [ "${WAIT_FOR_POSTGRES:-1}" = "1" ]; then
  wait_for_postgres
fi

exec "$@"
