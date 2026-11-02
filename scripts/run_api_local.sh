#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=services/api
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
export FIXTURE_MODE="${FIXTURE_MODE:-true}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:3000}"
python3 -m pip install -q -r services/api/requirements.txt
exec python3 -m uvicorn hypatia.app:app --host 0.0.0.0 --port "${PORT:-8000}" --app-dir services/api
