#!/usr/bin/env bash
# Set Vercel production API env and trigger redeploy (requires Vercel CLI logged in).
set -euo pipefail

API_BASE="${1:-${HYPATIA_API_URL:-}}"
if [[ -z "$API_BASE" ]]; then
  echo "Usage: $0 https://your-api.example.com" >&2
  exit 1
fi
API_BASE="${API_BASE%/}"
SCOPE="${VERCEL_SCOPE:-workshubhamdev-8920s-projects}"
WEB="${VERCEL_PRODUCTION_URL:-https://hypatia-chi.vercel.app}"

cd "$(dirname "$0")/../apps/web"
npx vercel link --yes --scope "$SCOPE" --project hypatia >/dev/null 2>&1 || true

add_env() {
  local key=$1 val=$2
  printf '%s' "$val" | npx vercel env add "$key" production preview development \
    --scope "$SCOPE" --force 2>/dev/null \
    || printf '%s' "$val" | npx vercel env add "$key" production --scope "$SCOPE" --force
}

echo "Setting API_ORIGIN and NEXT_PUBLIC_API_ORIGIN → ${API_BASE}" >&2
add_env API_ORIGIN "$API_BASE"
add_env NEXT_PUBLIC_API_ORIGIN "$API_BASE"

echo "Redeploying production…" >&2
npx vercel deploy --prod --scope "$SCOPE" --yes

echo ""
echo "Public lab: ${WEB}"
echo "Health (via rewrite): ${WEB}/api/health"
echo "Ensure API CORS_ORIGINS includes: ${WEB}"
