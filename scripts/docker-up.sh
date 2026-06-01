#!/bin/sh
set -e
cd "$(dirname "$0")/.."
cp -n .env.example .env 2>/dev/null || true
docker compose down --remove-orphans 2>/dev/null || true
docker rm -f crypto_trader-frontend-realtime-1 crypto_trader-frontend-analytics-1 2>/dev/null || true
docker compose up -d --build --remove-orphans
echo ""
echo "UI: http://localhost:${FRONTEND_HOST_PORT:-5173}"
