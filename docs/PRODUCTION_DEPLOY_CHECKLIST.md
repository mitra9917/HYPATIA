# Production deploy checklist (Playbook #57 / issue #39)

Use with **`docs/DEPLOYMENT.md`** and **`docs/MODAL_INTEGRATION.md`**.

## Modal API

- [ ] `modal secret create hypatia-secrets` with `MODEL_API_KEY` (+ optional `AWS_*`, `DATABASE_URL`)
- [ ] `modal deploy services/api/modal_app.py`
- [ ] `curl -s "$MODAL_URL/api/health"` returns `"ok": true` in **<2s** (default health skips Meta ping)
- [ ] Optional live probe: `curl -s "$MODAL_URL/api/health?meta_ping=1"`

## Vercel web

- [ ] `API_ORIGIN` / rewrite target = Modal ASGI URL
- [ ] `NEXT_PUBLIC_API_ORIGIN` = same URL (avoids Next proxy timeouts on long `/run`)
- [ ] `CORS_ORIGINS` on API includes production Vercel hostname

## CI

- [ ] GitHub Actions secrets per `docs/GITHUB_ACTIONS_SECRETS.md`
- [ ] `./scripts/verify_github_actions_secrets.sh` passes locally

## Warm path

- [ ] Hit `/api/health` before demo
- [ ] Run one fixture session via `POST /api/sessions` + `POST …/run` on staging
