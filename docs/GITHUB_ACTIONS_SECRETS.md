# GitHub Actions secrets — Playbook **#51** / issue [**#49**](https://github.com/mitra9917/HYPATIA/issues/49)

Configure under **Settings → Secrets and variables → Actions** on `mitra9917/HYPATIA`.  
Comment on issue **#49**: `GH secrets configured` (no values).

## Required for Modal deploy workflow

| Secret | Purpose |
| --- | --- |
| `MODAL_TOKEN_ID` | Modal workspace token id |
| `MODAL_TOKEN_SECRET` | Modal workspace token secret |

Optional (extend later):

| Secret | Purpose |
| --- | --- |
| `MODEL_API_KEY` | Opt-in live Meta smoke on `main` only |
| `VERCEL_TOKEN` | Vercel CLI deploy |
| `VERCEL_ORG_ID` | Vercel scope |
| `VERCEL_PROJECT_ID` | HYPATIA web project |

## Workflows

| File | When it runs |
| --- | --- |
| `.github/workflows/ci.yml` | Every PR — **no** deploy secrets required (`FIXTURE_MODE=true`) |
| `.github/workflows/deploy.yml` | Manual **Deploy** + optional `main` when secrets present |

## Verify checklist (local)

```bash
bash scripts/verify_github_actions_secrets.sh
```

DoD: secrets exist in GitHub UI; deploy workflow is wired to read `MODAL_TOKEN_*` only at deploy time.
