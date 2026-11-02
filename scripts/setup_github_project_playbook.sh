#!/usr/bin/env bash
# Populate HYPATIA Build Playbook project (mitra9917 project #4).
set -euo pipefail
OWNER=mitra9917
PROJECT=4
REPO=HYPATIA

# Playbook order (issue numbers) — 67 steps
ORDER=(
  44 2 3 5 48 4 45 46 6 7 8 9
  10 11 50 56 12 13 51 14 55 15 18
  52 16 53 54 17
  19 20 21 22 58 23 57 59 24 25
  26 27 28 29 30 31 32 33 60 62 61
  47 49 34 35 36 37 64 39 66 63 40 67 65 41 42 43 38 68
)

step=0
for num in "${ORDER[@]}"; do
  step=$((step + 1))
  url="https://github.com/${OWNER}/${REPO}/issues/${num}"
  echo "[$step] adding #$num"
  gh project item-add "$PROJECT" --owner "$OWNER" --url "$url" >/dev/null 2>&1 || true
  gh project item-edit "$PROJECT" --owner "$OWNER" --url "$url" \
    --field "Status" --value "Todo" 2>/dev/null || \
  gh project item-edit "$PROJECT" --owner "$OWNER" --url "$url" \
    --field "Status" --value "Up next" 2>/dev/null || true
  gh project item-edit "$PROJECT" --owner "$OWNER" --url "$url" \
    --field "Playbook" --number "$step" 2>/dev/null || \
  gh project item-edit "$PROJECT" --owner "$OWNER" --url "$url" \
    --field "Playbook #" --number "$step" 2>/dev/null || true
done

echo "Done. Open: https://github.com/users/${OWNER}/projects/${PROJECT}"
