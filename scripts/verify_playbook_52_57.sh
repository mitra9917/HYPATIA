#!/usr/bin/env bash
# Playbooks #52–#57 — scaffold validation (no Modal deploy required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/services/api"
export PYTHONPATH=.
export FIXTURE_MODE=true
export MODEL_API_KEY=""

pytest tests/test_toolsmith.py tests/test_veritas.py tests/test_cells_domain.py tests/test_tool_library_api.py tests/test_demo_reliability_ops.py tests/test_integration_playbook_52_57.py -q

bash "$ROOT/scripts/verify_production_deploy_checklist.sh"

echo "OK playbooks 52–57 validation"
