#!/usr/bin/env bash
# Curl /api/health — use while API is running (local or compose).
set -euo pipefail
BASE="${1:-http://127.0.0.1:8000}"
QS=""
if [[ "${2:-}" == "meta" ]]; then
  QS="?meta_ping=1"
fi
curl -fsS "${BASE}/api/health${QS}" | python3 -m json.tool
