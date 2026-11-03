#!/usr/bin/env bash
# Deploy the HYPATIA API to a single AWS EC2 instance. No local Docker needed:
# the instance clones the public GitHub repo, builds the image, and runs it behind
# Caddy, which gets a free HTTPS cert for <ip>.sslip.io.
# Needs IAM: docs/iam/hypatia-deploy-policy.json. Reads secrets from .env.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[[ -f .env ]] || { echo "Missing .env" >&2; exit 1; }
set -a
# shellcheck disable=SC1091
source .env
set +a
unset AWS_PROFILE

REGION="${AWS_REGION:-ap-south-1}"

BRANCH="${HYPATIA_GIT_BRANCH:-main}"
REPO_URL="${HYPATIA_GIT_URL:-https://github.com/mitra9917/HYPATIA.git}"
WEB="${VERCEL_PRODUCTION_URL:-https://hypatia-chi.vercel.app}"
CORS="${WEB},http://localhost:3000,http://127.0.0.1:3000"
NAME="hypatia-api"
AWS="aws --region $REGION"

for v in MODEL_API_KEY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY; do
  [[ -n "${!v:-}" ]] || { echo "Set $v in .env" >&2; exit 1; }
done

echo "Finding Amazon Linux 2023 AMI..." >&2
AMI="$($AWS ec2 describe-images --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023.*-x86_64" "Name=state,Values=available" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)"

VPC="$($AWS ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)"
[[ "$VPC" != "None" ]] || { echo "No default VPC in $REGION" >&2; exit 1; }

SG="$($AWS ec2 describe-security-groups --filters "Name=group-name,Values=${NAME}-sg" "Name=vpc-id,Values=$VPC" \
  --query 'SecurityGroups[0].GroupId' --output text)"
if [[ "$SG" == "None" ]]; then
  SG="$($AWS ec2 create-security-group --group-name "${NAME}-sg" --description "HYPATIA API web" --vpc-id "$VPC" \
    --query GroupId --output text)"
  for port in 80 443; do
    $AWS ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port "$port" --cidr 0.0.0.0/0 >/dev/null
  done
fi

# Stable public IP so the sslip.io hostname survives redeploys.
EIP_ALLOC="$($AWS ec2 describe-addresses --filters "Name=tag:Name,Values=$NAME" \
  --query 'Addresses[0].AllocationId' --output text)"
if [[ "$EIP_ALLOC" == "None" ]]; then
  EIP_ALLOC="$($AWS ec2 allocate-address --domain vpc \
    --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value=$NAME}]" \
    --query AllocationId --output text)"
fi
IP="$($AWS ec2 describe-addresses --allocation-ids "$EIP_ALLOC" --query 'Addresses[0].PublicIp' --output text)"
DOMAIN="${IP//./-}.sslip.io"
API_URL="https://${DOMAIN}"
echo "Public hostname: $DOMAIN" >&2

OLD="$($AWS ec2 describe-instances \
  --filters "Name=tag:Name,Values=$NAME" "Name=instance-state-name,Values=pending,running,stopped,stopping" \
  --query 'Reservations[].Instances[].InstanceId' --output text)"
if [[ -n "$OLD" ]]; then
  echo "Replacing existing instance: $OLD" >&2
  # shellcheck disable=SC2086
  $AWS ec2 terminate-instances --instance-ids $OLD >/dev/null
  # shellcheck disable=SC2086
  $AWS ec2 wait instance-terminated --instance-ids $OLD
fi

UD="$(mktemp)"
trap 'rm -f "$UD"' EXIT
cat >"$UD" <<EOF
#!/bin/bash
set -ex
exec > >(tee /var/log/hypatia-bootstrap.log) 2>&1
dnf install -y docker git
systemctl enable --now docker
cat > /opt/hypatia.env <<'ENVEOF'
MODEL_API_KEY=${MODEL_API_KEY}
META_BASE_URL=${META_BASE_URL:-https://api.meta.ai/v1}
FIXTURE_MODE=${FIXTURE_MODE:-true}
GLIMMER_PROVIDER=${GLIMMER_PROVIDER:-stub}
CORS_ORIGINS=${CORS}
AWS_REGION=${REGION}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
S3_BUCKET=${S3_BUCKET:-}
DATABASE_URL=${DATABASE_URL:-}
PORT=8000
ENVEOF
chmod 600 /opt/hypatia.env
git clone --depth 1 --branch ${BRANCH} ${REPO_URL} /opt/hypatia-src
cd /opt/hypatia-src
docker build -f services/api/Dockerfile -t hypatia-api .
docker run -d --name hypatia-api --restart always --env-file /opt/hypatia.env -p 127.0.0.1:8000:8000 hypatia-api
cat > /opt/Caddyfile <<'CADDY'
${DOMAIN} {
  reverse_proxy 127.0.0.1:8000 {
    flush_interval -1
  }
}
CADDY
docker run -d --name caddy --restart always --network host \
  -v /opt/Caddyfile:/etc/caddy/Caddyfile -v caddy_data:/data caddy:2
EOF

# Free-plan AWS accounts only allow "free-tier eligible" types, so try several.
# Set HYPATIA_EC2_TYPE to force one. The first with 4 GB+ RAM is the safest for the API.
if [[ -n "${HYPATIA_EC2_TYPE:-}" ]]; then
  CANDIDATES=("$HYPATIA_EC2_TYPE")
else
  CANDIDATES=(c7i-flex.large m7i-flex.large t3.small t3.medium t3.micro)
fi
IID=""
for ITYPE in "${CANDIDATES[@]}"; do
  echo "Trying $ITYPE..." >&2
  if IID="$($AWS ec2 run-instances --image-id "$AMI" --instance-type "$ITYPE" \
    --security-group-ids "$SG" --user-data "file://$UD" \
    --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3}' \
    --metadata-options 'HttpTokens=required,HttpEndpoint=enabled' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME}]" \
    --query 'Instances[0].InstanceId' --output text 2>/tmp/hypatia-run-instances.err)"; then
    echo "Launched $ITYPE as $IID" >&2
    break
  fi
  echo "  $ITYPE not allowed: $(tail -c 160 /tmp/hypatia-run-instances.err | tr '\n' ' ')" >&2
  IID=""
done
[[ -n "$IID" ]] || { echo "No instance type could be launched. See /tmp/hypatia-run-instances.err" >&2; exit 1; }
$AWS ec2 wait instance-running --instance-ids "$IID"
$AWS ec2 associate-address --instance-id "$IID" --allocation-id "$EIP_ALLOC" >/dev/null
echo "Instance $IID is up at $IP. Waiting for the image build and HTTPS (about 5-10 min)..." >&2

for _ in $(seq 1 90); do
  if curl -fsS -m 10 "${API_URL}/api/health" 2>/dev/null | grep -q '"ok":true'; then
    echo "" >&2
    echo "HYPATIA_API_URL=${API_URL}"
    exit 0
  fi
  sleep 10
done
echo "Timed out. Instance $IID may still be building. Retry: curl -s ${API_URL}/api/health" >&2
exit 1
