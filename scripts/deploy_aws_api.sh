#!/usr/bin/env bash
# Deploy HYPATIA FastAPI to AWS App Runner (Modal fallback when spend limit hit).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

REGION="${AWS_REGION:-ap-south-1}"
REPO_NAME="${HYPATIA_ECR_REPO:-hypatia-api}"
SERVICE_NAME="${HYPATIA_APP_RUNNER_SERVICE:-hypatia-api}"
VERCEL_WEB="${VERCEL_PRODUCTION_URL:-https://hypatia-chi.vercel.app}"
export CORS_ORIGINS="${CORS_ORIGINS:-$VERCEL_WEB,http://localhost:3000,http://127.0.0.1:3000}"

for v in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY MODEL_API_KEY; do
  if [[ -z "${!v:-}" ]]; then
    echo "Set $v in .env" >&2
    exit 1
  fi
done

ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" >/dev/null 2>&1 \
  || aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION" >/dev/null

aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"

echo "Building API image…" >&2
docker build -f services/api/Dockerfile -t "${REPO_NAME}:latest" .
docker tag "${REPO_NAME}:latest" "${ECR_URI}:latest"
docker push "${ECR_URI}:latest"

ACCESS_ROLE="$(aws iam get-role --role-name AppRunnerECRAccessRole --query Role.Arn --output text 2>/dev/null || true)"
if [[ -z "$ACCESS_ROLE" || "$ACCESS_ROLE" == "None" ]]; then
  aws iam create-role --role-name AppRunnerECRAccessRole \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"build.apprunner.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null 2>&1 || true
  aws iam attach-role-policy --role-name AppRunnerECRAccessRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess >/dev/null 2>&1 || true
  ACCESS_ROLE="$(aws iam get-role --role-name AppRunnerECRAccessRole --query Role.Arn --output text)"
fi

export ACCESS_ROLE ECR_URI
python3 <<'PY' >/tmp/hypatia-apprunner-source.json
import json, os
env = {
    "MODEL_API_KEY": os.environ["MODEL_API_KEY"],
    "META_BASE_URL": os.environ.get("META_BASE_URL", "https://api.meta.ai/v1"),
    "FIXTURE_MODE": os.environ.get("FIXTURE_MODE", "true"),
    "GLIMMER_PROVIDER": os.environ.get("GLIMMER_PROVIDER", "stub"),
    "CORS_ORIGINS": os.environ.get("CORS_ORIGINS", "*"),
    "AWS_REGION": os.environ.get("AWS_REGION", "ap-south-1"),
    "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
    "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
}
if os.environ.get("S3_BUCKET"):
    env["S3_BUCKET"] = os.environ["S3_BUCKET"]
if os.environ.get("DATABASE_URL"):
    env["DATABASE_URL"] = os.environ["DATABASE_URL"]
print(json.dumps({
    "AuthenticationConfiguration": {"AccessRoleArn": os.environ["ACCESS_ROLE"]},
    "AutoDeploymentsEnabled": False,
    "ImageRepository": {
        "ImageIdentifier": os.environ["ECR_URI"] + ":latest",
        "ImageRepositoryType": "ECR",
        "ImageConfiguration": {
            "Port": "8000",
            "RuntimeEnvironmentVariables": env,
        },
    },
}))
PY

SERVICE_ARN="$(aws apprunner list-services --region "$REGION" --query "ServiceSummaryList[?ServiceName=='${SERVICE_NAME}'].ServiceArn | [0]" --output text 2>/dev/null || true)"

if [[ -z "$SERVICE_ARN" || "$SERVICE_ARN" == "None" ]]; then
  echo "Creating App Runner service ${SERVICE_NAME}…" >&2
  SERVICE_ARN="$(aws apprunner create-service --region "$REGION" \
    --service-name "$SERVICE_NAME" \
    --source-configuration "file:///tmp/hypatia-apprunner-source.json" \
    --instance-configuration '{"Cpu":"1024","Memory":"2048"}' \
    --health-check-configuration '{"Protocol":"HTTP","Path":"/api/health","Interval":10,"Timeout":5,"HealthyThreshold":1,"UnhealthyThreshold":5}' \
    --query Service.ServiceArn --output text)"
else
  echo "Updating App Runner service…" >&2
  aws apprunner update-service --region "$REGION" --service-arn "$SERVICE_ARN" \
    --source-configuration "file:///tmp/hypatia-apprunner-source.json" >/dev/null
  aws apprunner start-deployment --region "$REGION" --service-arn "$SERVICE_ARN" >/dev/null
fi

echo "Waiting for RUNNING…" >&2
for _ in $(seq 1 90); do
  read -r STATUS URL < <(aws apprunner describe-service --region "$REGION" --service-arn "$SERVICE_ARN" \
    --query 'Service.[Status,ServiceUrl]' --output text)
  if [[ "$STATUS" == "RUNNING" && -n "$URL" && "$URL" != "None" ]]; then
    API_BASE="https://${URL}"
    curl -fsS "${API_BASE}/api/health" | head -c 120
    echo ""
    echo "HYPATIA_API_URL=${API_BASE}"
    exit 0
  fi
  sleep 10
done
echo "Timed out — check App Runner console for ${SERVICE_NAME}" >&2
exit 1
