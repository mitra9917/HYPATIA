#!/usr/bin/env bash
# Deploy HYPATIA API to Modal using repo-root .env (never commit secrets).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.example and fill MODEL_API_KEY + MODAL_TOKEN_*" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

for v in MODAL_TOKEN_ID MODAL_TOKEN_SECRET MODEL_API_KEY; do
  if [[ -z "${!v:-}" ]]; then
    echo "Set $v in .env before deploy" >&2
    exit 1
  fi
done

VERCEL_WEB="${VERCEL_PRODUCTION_URL:-https://hypatia-chi.vercel.app}"
CORS="${CORS_ORIGINS:-$VERCEL_WEB,http://localhost:3000,http://127.0.0.1:3000}"

modal token set --token-id "$MODAL_TOKEN_ID" --token-secret "$MODAL_TOKEN_SECRET" >/dev/null

modal volume create hypatia-weights 2>/dev/null || true

SECRET_ARGS=(
  "MODEL_API_KEY=${MODEL_API_KEY}"
  "META_BASE_URL=${META_BASE_URL:-https://api.meta.ai/v1}"
  "FIXTURE_MODE=${FIXTURE_MODE:-true}"
  "GLIMMER_PROVIDER=${GLIMMER_PROVIDER:-modal}"
  "CORS_ORIGINS=${CORS}"
)

if [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" && -n "${S3_BUCKET:-}" ]]; then
  SECRET_ARGS+=(
    "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
    "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"
    "AWS_REGION=${AWS_REGION:-ap-south-1}"
    "S3_BUCKET=${S3_BUCKET}"
  )
fi

if [[ -n "${DATABASE_URL:-}" ]]; then
  SECRET_ARGS+=("DATABASE_URL=${DATABASE_URL}")
fi

echo "Creating/updating Modal secret hypatia-secrets…" >&2
# shellcheck disable=SC2068
modal secret create hypatia-secrets "${SECRET_ARGS[@]}" --force

echo "Deploying Modal app…" >&2
modal deploy services/api/modal_app.py

echo "" >&2
echo "Resolve API base URL:" >&2
modal app list 2>/dev/null | awk '/hypatia/ {print "  " $0}' >&2 || true
