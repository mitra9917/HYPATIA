#!/usr/bin/env bash
# AWS-only production deploy: API on EC2 (no local Docker), then wire Vercel.
# App Runner is not available on this AWS account (SubscriptionRequiredException).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
bash scripts/deploy_aws_ec2.sh 2>&1 | tee /tmp/hypatia-aws-deploy.log
API_URL="$(grep -oE 'HYPATIA_API_URL=https://[^ ]+' /tmp/hypatia-aws-deploy.log | cut -d= -f2- | head -1 || true)"
if [[ -n "$API_URL" ]]; then
  export HYPATIA_API_URL="$API_URL"
  bash scripts/vercel_wire_api.sh "$API_URL"
else
  echo "No API URL in log. Fix the AWS deploy first." >&2
  exit 1
fi
