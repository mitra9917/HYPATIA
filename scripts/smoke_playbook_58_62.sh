#!/usr/bin/env bash
# Docs + evals + cost report (no running API required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
bash "$ROOT/scripts/verify_playbook_58_62.sh"
echo "Optional live API: ./scripts/smoke_playbook_52_57.sh"
