# Production deploy — unblock checklist

**Policy:** **No Render** (any tier). Web = **Vercel**. API = **Modal** (Meta hackathon partner) or **AWS App Runner + S3** — not free-tier hobby hosts.

**Status (automated attempt):** Modal **`hypatia-secrets`** created; **`modal deploy` blocked** by workspace spend limit. AWS **`hypatia-cli`** lacks ECR/App Runner/S3 permissions. Vercel **frontend** deploys from GitHub; **API env vars not set** until backend URL exists.

## Path A — Modal (Meta hackathon priority)

1. [Modal billing](https://modal.com/settings/billing) → raise or reset **spend limit** for workspace `ac-iOl7AF2iAQt3JOSbKTOnad`.
2. From repo root:
   ```bash
   bash scripts/deploy_modal_prod.sh
   ```
3. Copy the printed `https://….modal.run` base URL.
4. Configure Vercel:
   ```bash
   export HYPATIA_API_URL=https://YOUR-MODAL-URL
   bash scripts/configure_vercel_prod.sh
   ```
   Or use Vercel dashboard → **hypatia** → Environment Variables → Production:
   - `API_ORIGIN` = Modal URL  
   - `NEXT_PUBLIC_API_ORIGIN` = same URL  
5. Redeploy web (push to `main` or Redeploy in Vercel).
6. Smoke:
   ```bash
   curl -s "https://hypatia-chi.vercel.app/api/health"
   ./scripts/smoke_playbook_52_57.sh   # BASE=Modal URL
   ```

Optional: GitHub secrets `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`, `HYPATIA_API_URL`; run **Deploy** workflow with **dry_run = false**.

## Path B — AWS App Runner + S3 (when Modal blocked — **use this, not Render**)

Attach **`docs/iam/hypatia-deploy-policy.json`** to IAM user **`hypatia-cli`** (or run deploy via an admin role).

`scripts/deploy_aws_api.sh` uses **1 vCPU / 2 GiB** App Runner (not 512 MB free-tier boxes). Media goes to your **S3** bucket via env vars, not ephemeral disk.

```bash
bash scripts/deploy_aws_api.sh
export HYPATIA_API_URL=https://….ap-south-1.awsapprunner.com
bash scripts/configure_vercel_prod.sh
```

Ensure **`CORS_ORIGINS`** on the API includes `https://hypatia-chi.vercel.app`.

## Vercel public access

If judges hit **Vercel Authentication**, disable **Deployment Protection** on production:
Vercel → **hypatia** → Settings → Deployment Protection → allow public access to production / custom domain.

## AWS S3 (uploads / media)

Bucket in `.env` is configured; **`hypatia-cli`** needs `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` on that bucket. Keys are already in Modal secret when using Path A.

## After both tiers are live

Update [`docs/SUBMISSION_PACK.md`](SUBMISSION_PACK.md) **Live demo** row and README public URL line, then record demo video + portal submission.
