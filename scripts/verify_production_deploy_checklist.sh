#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for f in docs/PRODUCTION_DEPLOY_CHECKLIST.md docs/DEMO_RELIABILITY.md docs/DEPLOYMENT.md .github/workflows/deploy.yml; do
  test -f "$ROOT/$f" || { echo "missing $f" >&2; exit 1; }
done
grep -q "CORS_ORIGINS" "$ROOT/docs/PRODUCTION_DEPLOY_CHECKLIST.md"
grep -q "modal deploy" "$ROOT/docs/PRODUCTION_DEPLOY_CHECKLIST.md"
echo "production deploy checklist files present"
