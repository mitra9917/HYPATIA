#!/usr/bin/env bash
# Pre-judge smoke: stub Glimmer + optional live Wonder (needs .env keys).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/services/api"

echo "=== Glimmer (GLIMMER_PROVIDER from .env; use modal after deploy) ==="
python3 scripts/smoke_glimmer.py

echo ""
echo "=== Wonder PI (live only if MODEL_API_KEY set) ==="
python3 scripts/smoke_wonder_pi.py

echo ""
echo "Done. For modal Glimmer: modal deploy services/api/modal_app.py && GLIMMER_PROVIDER=modal"
