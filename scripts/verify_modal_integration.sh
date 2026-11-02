#!/usr/bin/env bash
# Playbook #50 / issue #47 — verify Modal volume + secret scaffold (no secret values printed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== modal_app.py syntax ==="
python3 -c "import ast; ast.parse(open('services/api/modal_app.py').read()); print('ok')"

echo "=== hypatia-weights + hypatia-secrets references ==="
grep -q 'hypatia-weights' services/api/modal_app.py
grep -q 'hypatia-secrets' services/api/modal_app.py
echo "ok"

if ! command -v modal >/dev/null 2>&1; then
  echo "SKIP: modal CLI not installed (pip install modal). Scaffold OK for CI."
  exit 0
fi

echo "=== modal profile ==="
modal profile current 2>/dev/null || { echo "WARN: run modal setup"; exit 0; }

if [[ "${MODAL_INTEGRATION_VERIFY_LIVE:-}" != "1" ]]; then
  echo "SKIP: cloud volume/secret check (set MODAL_INTEGRATION_VERIFY_LIVE=1 after you create them)"
  echo "Done."
  exit 0
fi

echo "=== modal volume list (hypatia-weights) ==="
if modal volume list 2>/dev/null | grep -q hypatia-weights; then
  echo "ok: hypatia-weights"
else
  echo "WARN: run: modal volume create hypatia-weights"
fi

echo "=== modal secret list (hypatia-secrets) ==="
if modal secret list 2>/dev/null | grep -q hypatia-secrets; then
  echo "ok: hypatia-secrets"
else
  echo "WARN: run modal secret create hypatia-secrets (see docs/MODAL_INTEGRATION.md)"
fi

echo "Done."
