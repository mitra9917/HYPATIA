#!/usr/bin/env bash
# Install API deps so local measure→hypothesize matches CI (includes meta_sam_parser).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m pip install -r "$ROOT/services/api/requirements.txt" pytest
echo "OK. Run: export PYTHONPATH=$ROOT/services/api && pytest services/api/tests/test_orchestrator.py -q"
