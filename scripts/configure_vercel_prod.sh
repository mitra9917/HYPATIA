#!/usr/bin/env bash
# Set Vercel production env for HYPATIA lab (run after API is live).
set -euo pipefail

API_BASE="${1:-${HYPATIA_API_URL:-}}"
if [[ -z "$API_BASE" ]]; then
  echo "Usage: HYPATIA_API_URL=https://….modal.run $0" >&2
  echo "   or: $0 https://….modal.run" >&2
  exit 1
fi
API_BASE="${API_BASE%/}"

PROJECT="${VERCEL_PROJECT_ID:-prj_YU05W3LC1LZRg0wt1h2Fl61Kfuvz}"
TEAM="${VERCEL_TEAM_ID:-team_xPcskqV5RGnr1aKzJ9AvwyY5}"

echo "Set in Vercel → hypatia → Settings → Environment Variables (Production):"
echo "  API_ORIGIN=${API_BASE}"
echo "  NEXT_PUBLIC_API_ORIGIN=${API_BASE}"
echo ""
echo "Then redeploy production (Deployments → … → Redeploy) or push to main."
echo ""
echo "On Modal/AWS secret / API env, ensure CORS includes:"
  echo "  https://hypatia-chi.vercel.app"
echo "  (and your custom domain if any)"
