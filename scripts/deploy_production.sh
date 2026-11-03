#!/usr/bin/env bash
# Production: Modal first (Meta hackathon partner), AWS App Runner if Modal spend limit blocks.
# Never Render — see docs/DEPLOY_LIVE_NOW.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== HYPATIA production deploy ===" >&2

if bash scripts/deploy_modal_prod.sh 2>&1 | tee /tmp/hypatia-modal-deploy.log; then
  MODAL_URL="$(grep -oE 'https://[a-zA-Z0-9.-]+\.modal\.run' /tmp/hypatia-modal-deploy.log | head -1 || true)"
  if [[ -z "$MODAL_URL" ]]; then
    MODAL_URL="$(modal app list 2>/dev/null | grep -oE 'https://[^ ]+' | head -1 || true)"
  fi
  if [[ -n "$MODAL_URL" ]]; then
    export HYPATIA_API_URL="$MODAL_URL"
    bash scripts/configure_vercel_prod.sh "$MODAL_URL"
    exit 0
  fi
fi

echo "Modal deploy failed — trying AWS App Runner…" >&2
if bash scripts/deploy_aws_api.sh; then
  exit 0
fi

echo "" >&2
echo "Both paths failed. See docs/DEPLOY_LIVE_NOW.md" >&2
exit 1
