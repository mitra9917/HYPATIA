#!/usr/bin/env bash
# Playbook #51 / issue #49 — checklist for GitHub Actions secrets (does not read GitHub API).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docs="docs/GITHUB_ACTIONS_SECRETS.md"
workflow=".github/workflows/deploy.yml"

test -f "$docs"
test -f "$workflow"

for name in MODAL_TOKEN_ID MODAL_TOKEN_SECRET; do
  grep -q "$name" "$docs" || { echo "missing doc mention: $name"; exit 1; }
  grep -q "$name" "$workflow" || { echo "missing workflow mention: $name"; exit 1; }
done

echo "ok: deploy workflow + docs reference MODAL_TOKEN_ID and MODAL_TOKEN_SECRET"
echo "Human DoD: add secrets in GitHub Settings → Actions, then comment on issue #49."
