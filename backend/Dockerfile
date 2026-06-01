FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml backend/README.md /app/backend/
COPY backend/src /app/backend/src
COPY infra/migrations /app/infra/migrations

RUN pip install --no-cache-dir /app/backend

ENV PYTHONPATH=/app/backend/src
ENV PYTHONUNBUFFERED=1

COPY infra/scripts /app/infra/scripts
COPY infra/scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /app/infra/scripts/*.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
