#!/usr/bin/env bash
# Playbooks #58–#62 — docs, evals, cost report, CI scaffold validation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f docs/HACKATHON_ALIGNMENT.md
test -f docs/FINALS_WARM.md
test -f docs/META_EVIDENCE.md
test -f meta_evidence.json
test -f scripts/cost_report.py
test -f .github/workflows/warm-health.yml
grep -q "min_containers" services/api/modal_app.py
grep -q "MODAL_FINALS_WARM" services/api/modal_app.py

python3 scripts/cost_report.py --json | python3 -c "import sys,json; r=json.load(sys.stdin); assert r['meta_calls']>0; assert r['budget_usd']==150"

python3 -m evals --suite desk-mechanics --mode fixture
test -f evals/results/$(date -u +%Y%m%d)_summary.md || test -n "$(ls evals/results/*_summary.md 2>/dev/null | head -1)"

cd services/api
export PYTHONPATH=.
export FIXTURE_MODE=true
export MODEL_API_KEY=""
pytest tests/test_integration_playbook_58_62.py -q

echo "OK playbooks 58–62 validation"
