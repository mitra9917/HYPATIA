# Deployment Plan

HYPATIA must be **alive and boringly reliable** from submission through Nov 9 finals. Prefer boring infrastructure over cleverness.

## 1. Target topology

```text
                    Cloudflare / Render TLS
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     Web (Next.js)                     API (FastAPI)
     Render Static /                   Render Web Service
     Web Service                       bind 0.0.0.0:$PORT
              │                               │
              │         ┌─────────────────────┤
              │         ▼                     ▼
              │   Postgres (Render)     Redis (optional)
              │         │               job queue / SSE fanout
              │         ▼
              │   Disk OR R2/S3 for media
              │   (Render disk if single instance;
              │    object storage preferred)
              │
              └── Modal / Baseten (Glimmer + Toolsmith sandbox)
```

### Why Render (primary)

- Team already has Render platform rules in workspace.
- Web services + Postgres + Blueprint (`render.yaml`) fit full-stack.
- Bind HTTP to `0.0.0.0:$PORT`.
- Ephemeral FS → **do not** rely on local disk across deploys; use Postgres + object storage / persistent disk carefully (single instance).

### Optional secondary

- **Vercel** for Next.js frontend only + Render/Modal for Python API (CORS + env wiring).
- Keep one URL in submission to avoid judge confusion.

## 2. Services

| Service | Runtime | Notes |
| --- | --- | --- |
| `hypatia-web` | Node 20 / Next.js | UI; can reverse-proxy API in same origin via rewrites |
| `hypatia-api` | Python 3.11+ / uvicorn | Agents, SAM orchestration, science |
| `hypatia-db` | Postgres 16 | Sessions, laws, library |
| `hypatia-worker` (optional) | same image as API | Long SAM / swarm jobs |
| Modal apps | Python | Glimmer endpoint + Toolsmith sandbox |

## 3. Environment variables

```bash
# Meta
MODEL_API_KEY=
META_BASE_URL=https://api.meta.ai/v1
META_OBSERVER_MODEL=muse-spark-1.3
META_PI_MODEL=muse-wonder-1.0
META_IMAGE_MODEL=muse-image-1.0
META_SAM_MODEL=sam-3.1
META_VOICE_MODEL=muse-voice-transcribe-1.0
META_USE_CONTRIBUTOR=false   # true only for non-sensitive loops

# App
DATABASE_URL=
REDIS_URL=                   # optional
MEDIA_BUCKET_URL=            # s3/r2 or file:///data/media for disk
FIXTURE_MODE=false           # true for guaranteed demo
CORS_ORIGINS=https://hypatia.onrender.com

# Partners
MODAL_TOKEN_ID=
MODAL_TOKEN_SECRET=
BASETEN_API_KEY=             # optional Glimmer host
```

Never commit secrets. Use Render Env Groups for shared Meta key across web/api if needed (prefer API-only key usage; web talks to our API).

## 4. `render.yaml` sketch

```yaml
services:
  - type: web
    name: hypatia-api
    runtime: python
    plan: starter
    buildCommand: pip install -r services/api/requirements.txt
    startCommand: uvicorn hypatia.app:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hypatia-db
          property: connectionString
      - key: MODEL_API_KEY
        sync: false

  - type: web
    name: hypatia-web
    runtime: node
    buildCommand: cd apps/web && npm ci && npm run build
    startCommand: cd apps/web && npm run start -- --hostname 0.0.0.0 --port $PORT
    envVars:
      - key: NEXT_PUBLIC_API_URL
        fromService:
          name: hypatia-api
          type: web
          property: host

databases:
  - name: hypatia-db
    plan: free   # note: free DB expires ~30d — fine for hackathon window
```

**Free-tier reality:** web services spin down after ~15 minutes idle. Mitigations:

1. External uptime ping every 10 minutes during judging (Nov 4–9).
2. Or paid starter for the judging window.
3. Demo video remains the primary artifact either way.

## 5. Media strategy (ephemeral FS)

| Approach | Use when |
| --- | --- |
| Render persistent disk mounted at `/data` | Single-instance API, simplest |
| Cloudflare R2 / S3 | Multi-instance or diskless |
| Pre-uploaded Meta Files API `file_id`s | Demo clips — **best for finals** |

Ship `scripts/warm_meta_files.py` to upload pendulum/cells/fake clips once and store IDs in Postgres / env.

## 6. CI / CD

GitHub Actions:

1. `lint` — ruff + eslint
2. `test` — unit science gates + API contract tests with fixtures (no live Meta spend)
3. `smoke` — optional nightly live Meta call gated by secret
4. On push to `main`: auto-deploy Render (Blueprint sync)

## 7. Demo reliability modes

| Mode | Behavior |
| --- | --- |
| `live` | Real Meta API |
| `hybrid` | Live Spark/Wonder; cached SAM tracks |
| `fixture` | Full offline replay of a known-good session |

UI shows a small mode chip. For recorded demo video: prefer `live` or `hybrid`. For finals: start `hybrid`, fall back `fixture` in <5s.

## 8. Launch checklist (submit day)

- [ ] `GET /api/health` 200 from public URL
- [ ] Create session → observe → measure on pendulum fixture under 60s
- [ ] Ghost overlay renders
- [ ] Env vars present on Render (no missing MODEL_API_KEY)
- [ ] Postgres migrations applied
- [ ] Uptime robot pointed at health
- [ ] README links: live app, demo video, architecture
- [ ] Cost dashboard screenshot archived
- [ ] Secondary laptop with `docker compose up` offline bundle

## 9. Local docker path

```bash
docker compose up --build
# web :3000  api :8000  postgres :5432
```

Identical feature flags as production (`FIXTURE_MODE` supported).

## 10. Partner compute

| Need | Platform |
| --- | --- |
| Glimmer 30B-class serving | Baseten / Fireworks / Modal GPU |
| Toolsmith isolated exec | Modal Sandbox (preferred) or Docker-in-Docker on worker |
| Open SAM weights fallback | Modal GPU endpoint |

Keep partner usage behind interfaces: `HypothesisSwarm`, `SandboxRunner` so local CPU stubs work in CI.

## 11. Domain / branding

- Temporary: `hypatia-xxxx.onrender.com`
- Optional custom domain if available before video shoot (nice, not required)
- OG image with tagline for link unfurls when sharing the viral clip
