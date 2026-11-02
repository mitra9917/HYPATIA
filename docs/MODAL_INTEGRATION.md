# Modal integration — Playbook **#50** / issue [**#47**](https://github.com/mitra9917/HYPATIA/issues/47)

One-time setup before production deploy (`docs/DEPLOYMENT.md` §5). **Never commit secret values.**

## 1. CLI auth

```bash
pip install modal
modal setup   # or: modal token set --token-id "$MODAL_TOKEN_ID" --token-secret "$MODAL_TOKEN_SECRET"
modal profile current
```

## 2. Volume (weights + fixture cache)

```bash
modal volume create hypatia-weights
modal volume list | grep hypatia-weights
```

Mounted in `services/api/modal_app.py` at **`/weights`**.

## 3. Secret `hypatia-secrets`

```bash
modal secret create hypatia-secrets \
  MODEL_API_KEY=... \
  DATABASE_URL=... \
  AWS_ACCESS_KEY_ID=... \
  AWS_SECRET_ACCESS_KEY=... \
  AWS_REGION=ap-south-1 \
  S3_BUCKET=... \
  GLIMMER_PROVIDER=modal \
  FIXTURE_MODE=false
```

Verify:

```bash
modal secret list | grep hypatia-secrets
```

Comment on issue **#47**: `secrets created in Modal` (no values).

## 4. S3 mount prep

When `AWS_*` and `S3_BUCKET` are in `hypatia-secrets`, enable the optional **`CloudBucketMount`** block documented in `services/api/modal_app.py` (media at `/media`). Until then, API uses boto3 uploads from env (same keys in secret).

## 5. Deploy

```bash
modal deploy services/api/modal_app.py
curl -s "$(modal app list | awk '/hypatia/{print $2}')/api/health" | head
```

## 6. Repo verifier (CI + local)

```bash
bash scripts/verify_modal_integration.sh
```

Optional after you create volume/secret in Modal:

```bash
MODAL_INTEGRATION_VERIFY_LIVE=1 bash scripts/verify_modal_integration.sh
```

DoD: `modal secret list` shows **`hypatia-secrets`** and volume **`hypatia-weights`** exists (human step); repo script + tests prove scaffold is ready.
