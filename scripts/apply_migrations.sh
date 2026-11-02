#!/usr/bin/env bash
# Apply SQL migrations when DATABASE_URL is set (see docker-compose api service).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=services/api
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
exec python3 -m hypatia.db migrate "$@"
