#!/usr/bin/env bash
# Run the Next.js lab UI — use a dedicated terminal tab (do not source).
set -euo pipefail

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  echo "Run: ./scripts/run_web_local.sh" >&2
  return 1 2>/dev/null || exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}/apps/web"

if lsof -ti :3000 >/dev/null 2>&1; then
  echo "Port 3000 already in use. Stop the other Next process first." >&2
  exit 1
fi

# Stale mix of `next build` + `next dev` leaves empty .next/static/css/app → unstyled white page.
rm -rf .next

echo "HYPATIA web → http://localhost:3000  (Ctrl+C to stop)" >&2
echo "Keep ./scripts/run_api_local.sh running in another tab for the lab." >&2
echo "Do not run 'npm run build' while this dev server is up — it corrupts .next." >&2

npm run dev
