#!/usr/bin/env bash
# Ensure data/videos/SOURCES.md lists ≥8 rights-documented clips (Playbook #28 / #17).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCES="${ROOT}/data/videos/SOURCES.md"

if [[ ! -f "$SOURCES" ]]; then
  echo "Missing $SOURCES" >&2
  exit 1
fi

# Count table body rows: lines starting with | that are not header or separator.
count=$(awk '
  /^\|/ && !/^\| ---/ && !/^\| ID / && !/^\| File / { n++ }
  END { print n+0 }
' "$SOURCES")

min=8
if (( count < min )); then
  echo "SOURCES.md has $count catalogued clips; need ≥$min" >&2
  exit 1
fi

echo "OK: $count clips documented in data/videos/SOURCES.md"
