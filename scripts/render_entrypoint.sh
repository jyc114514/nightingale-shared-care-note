#!/bin/sh
set -eu

: "${PORT:=10000}"

# Validate production settings before touching the database. The command prints no secrets.
python -c 'from app.config import settings; settings.validate_runtime_security()'
alembic upgrade head

if [ "${DEMO_SEED_ENABLED:-false}" = "true" ]; then
  if [ -z "${DEMO_SEED_PASSWORD:-}" ]; then
    echo "DEMO_SEED_ENABLED=true requires a synthetic DEMO_SEED_PASSWORD" >&2
    exit 1
  fi
  python -m app.scripts.seed_demo
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
