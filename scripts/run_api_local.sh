#!/usr/bin/env bash
# Run the API in a dedicated terminal tab — do NOT `source` this file (see guard below).
set -euo pipefail

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  echo "Do not source this script — it would replace your interactive shell." >&2
  echo "Run:  ./scripts/run_api_local.sh" >&2
  return 1 2>/dev/null || exit 1
fi

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

trap 'code=$?; if (( code != 0 )); then echo >&2; echo "HYPATIA API exited ($code). Fix errors above, then: ./scripts/run_api_local.sh" >&2; fi' EXIT

python3 -m pip install -q -r services/api/requirements.txt
echo "HYPATIA API → http://127.0.0.1:${PORT:-8000}/api/health  (Ctrl+C to stop)" >&2
python3 -m uvicorn hypatia.app:app --host 0.0.0.0 --port "${PORT:-8000}" --app-dir services/api
