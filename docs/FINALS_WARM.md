# Finals warm containers (Playbook #58 / issue #66)

During **judging Nov 4–9, 2026 (ET)**, keep Modal API containers warm so cold start **p95 &lt; 3s**.

## Modal deploy

```bash
export MODAL_FINALS_WARM=1   # only during finals window — costs money
modal deploy services/api/modal_app.py
```

`services/api/modal_app.py` sets `min_containers=1` on the FastAPI ASGI function when `MODAL_FINALS_WARM` is truthy. **Turn off after Nov 9** to save credits.

## Health ping (keep-alive)

- **GitHub Actions:** [`.github/workflows/warm-health.yml`](../.github/workflows/warm-health.yml) — workflow_dispatch or cron during finals
- **Secrets:** `HYPATIA_API_URL` = public Modal ASGI base (no trailing slash)
- **Endpoint:** `GET /api/health` (fast; Meta ping optional via `?meta_ping=1`)

## CORS recheck after warm

Ensure `CORS_ORIGINS` on Modal secret / env includes:

- `https://<your-vercel-app>.vercel.app`
- `http://localhost:3000` for rehearsal

Web must set `NEXT_PUBLIC_API_ORIGIN` to the Modal URL (not Next rewrite) for long `/run` stages.

## DoD

- [ ] Documented ping + warm flag (this file)
- [ ] Smoke: `time curl -s "$HYPATIA_API_URL/api/health" | head -c 80` consistently &lt; 3s during warm window
