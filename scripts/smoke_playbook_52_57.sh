#!/usr/bin/env bash
# Live API smoke for playbooks 52–57 — run while ./scripts/run_api_local.sh is up.
# Usage: ./scripts/smoke_playbook_52_57.sh
#        BASE=http://127.0.0.1:8000 ./scripts/smoke_playbook_52_57.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${BASE:-${API:-http://127.0.0.1:8000}}"
BASE="${BASE%/}"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

curl_json() {
  local method="$1"
  local path="$2"
  shift 2
  local tmp
  tmp="$(mktemp)"
  local code
  code="$(curl -sS --max-time 120 -o "$tmp" -w "%{http_code}" -X "$method" "$@" "${BASE}${path}")" \
    || fail "curl could not reach ${BASE}${path} — start API: ./scripts/run_api_local.sh"
  if [[ "$code" != "200" && "$code" != "201" ]]; then
    echo "HTTP $code from ${BASE}${path}:" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    fail "unexpected status"
  fi
  if ! python3 -m json.tool "$tmp" >/dev/null 2>&1; then
    echo "Non-JSON from ${BASE}${path} (HTTP $code):" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    fail "expected JSON — is the API on branch with playbooks 52–57? (restart run_api_local.sh)"
  fi
  cat "$tmp"
  rm -f "$tmp"
}

echo "HYPATIA smoke playbooks 52–57 → ${BASE}"
echo "(Set BASE or API if not using default 127.0.0.1:8000)"
echo

echo "→ health"
health="$(curl_json GET "/api/health")"
echo "$health" | python3 -c "import sys,json; h=json.load(sys.stdin); assert h.get('ok') is True, h"
echo "  ok"

echo "→ prep: ops fixture (fast observe/cells; avoids live Meta hangs)"
curl_json POST "/api/ops/mode" -H "Content-Type: application/json" -d '{"mode":"fixture"}' >/dev/null
echo "  ok"

echo "→ #52 Toolsmith"
ts="$(curl_json POST "/api/toolsmith/test-promoted")"
echo "$ts" | python3 -c "import sys,json; b=json.load(sys.stdin); assert b.get('ok') is True, b; assert b.get('returncode')==0, b"
echo "  ok"

echo "→ #53 tool library"
lib="$(curl_json GET "/api/library/tools")"
echo "$lib" | python3 -c "import sys,json; b=json.load(sys.stdin); assert b.get('count',0)>=1, b"
echo "  ok"

echo "→ #54 cells"
SID="$(curl_json POST "/api/sessions?domain_hint=biology.cells" | python3 -c "import sys,json; print(json.load(sys.stdin)['session']['id'])")"
curl_json POST "/api/sessions/${SID}/observe" | python3 -c "import sys,json; s=json.load(sys.stdin)['session']; assert s['scene']['suggested_domain']=='biology.cells'"
nb_tmp="$(mktemp)"
code="$(curl -sS -o "$nb_tmp" -w "%{http_code}" "${BASE}/api/sessions/${SID}/cells-notebook.md")"
[[ "$code" == "200" ]] || fail "cells-notebook HTTP $code"
grep -Eiq 'logistic|N\(t\)' "$nb_tmp" || fail "cells notebook missing logistic growth"
rm -f "$nb_tmp"
echo "  ok"

echo "→ #55 VERITAS"
v="$(curl_json POST "/api/veritas/analyze")"
echo "$v" | python3 -c "import sys,json; b=json.load(sys.stdin); assert b.get('verdict')=='not_physical'; assert b.get('break_frame')==41"
echo "  ok"

echo "→ #56 ops fixture (already set at start; confirm)"
mode="$(curl_json GET "/api/health" | python3 -c "import sys,json; print(json.load(sys.stdin)['ops']['ops_mode'])")"
[[ "$mode" == "fixture" ]] || fail "expected ops_mode fixture, got $mode"
echo "  ok"

echo "→ #57 deploy checklist"
bash "$ROOT/scripts/verify_production_deploy_checklist.sh"

echo
echo "OK — all playbook 52–57 live smokes passed."
echo "Manual curls: export API=${BASE}"
