# Deployment Plan

HYPATIA must stay **alive and boringly reliable** from submission through Nov 9 finals — including when we run **heavy open-weight models** (Glimmer swarm, optional open SAM).

**Decision (updated):** do **not** use Render free tier as the primary host. Prefer a **Modal-first** stack for the API + GPUs + model storage, with a light frontend host and real object storage. AWS is a strong *post-hackathon / production* path, not the fastest way to win this week.

## 0. Recommendation (read this first)

| Option | Verdict for HYPATIA this week | Why |
| --- | --- | --- |
| **Modal (primary)** | **Choose this** | Hackathon partner (~$100 credits); serverless **GPUs**; durable **Volumes** for multi‑GB weights; **Sandboxes** for Toolsmith; FastAPI via web endpoints; scales to zero; Python-native |
| **Vercel (web UI)** | Use with Modal | Free/cheap Next.js hosting; zero ops; keep one public URL via rewrite/proxy |
| **Neon / Supabase Postgres** | Use | Real DB without Render’s free-DB expiry / size pain |
| **Cloudflare R2 or AWS S3** | Use for media | Cheap durable video/mask storage (not 512 MB disks) |
| **Baseten / Fireworks** | Optional GPU endpoints | Also partner credits; good if Glimmer serving is simpler as a managed endpoint |
| **AWS (ECS/EC2 + S3 + RDS)** | **Later / if you already know AWS** | Excellent scale & storage, but **Fargate has no GPU**; GPUs need EC2/SageMaker; IAM/VPC/ALB setup burns remaining days |
| **Render free** | **Avoid as primary** | Spin-down, tiny disk, ephemeral FS — fine maybe as a throwaway mirror, not for heavy models or judging week |
| **Fly.io / Railway** | Backup app host | Better than Render free for always-on API **without** GPU; still pair with Modal for weights |

### Why not “just AWS” right now?

- **Storage:** S3 is excellent — we still use S3/R2 either way.
- **Heavy models:** AWS Fargate **cannot** attach GPUs. You need EC2 GPU / SageMaker / EKS+GPU — more YAML, quotas, and bill surprise.
- **Time:** Indie deadline is **Nov 4, 9 PM ET**. Modal is code-defined (`@app.function(gpu=…)`) and already in the hackathon partner set. AWS wins for a long-lived company product; Modal wins for a 72-hour sustained demo with fat weights.

### Architecture implication (important)

Most “brain” calls stay on **Meta Model API** (Spark / Wonder / Image / SAM / Voice).  
Heavy local weight is mainly:

1. **Muse Glimmer** hypothesis swarm  
2. Optional **open SAM** fallback  
3. **Toolsmith** sandboxes + PySR jobs  
4. Cached videos / masks / fixtures  

So: keep Meta API for the wow path; put **only** the heavy bits on Modal GPUs + Volumes.

---

## 1. Target topology (Modal-first)

```text
                         Judges / demo laptop
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
           Vercel (Next.js)              Optional custom domain
           hypatia.vercel.app            (Cloudflare DNS)
                    │
                    │  /api/* rewrite  OR  NEXT_PUBLIC_API_URL
                    ▼
           Modal web endpoint (FastAPI)
           hypatia-api.modal.run
                    │
     ┌──────────────┼──────────────────┬────────────────────┐
     ▼              ▼                  ▼                    ▼
 Meta Model API   Modal GPU fns     Modal Volume         R2 / S3
 Spark/Wonder/    Glimmer swarm     (multi-GB weights,   (videos,
 Image/SAM/Voice  open-SAM opt.     fixture cache)        masks, notebooks)
                  Toolsmith sandbox
     │
     ▼
 Neon / Supabase Postgres
 (sessions, laws, library, meta file_ids)
```

**One submission URL:** prefer the Vercel app as the public face; it proxies API calls to Modal so judges never juggle two hosts.

---

## 2. Services

| Service | Where | Notes |
| --- | --- | --- |
| `hypatia-web` | **Vercel** | Next.js App Router; SSR/static as needed |
| `hypatia-api` | **Modal** `@modal.asgi_app()` / web endpoint | FastAPI orchestration, SSE, Meta client |
| `hypatia-glimmer` | Modal GPU function (A10/L4/A100 as needed) | Open-weights swarm; keep warm for demo window |
| `hypatia-toolsmith` | Modal **Sandbox** | Isolated code gen + tests |
| `hypatia-sam-local` (opt.) | Modal GPU | Only if Meta SAM is slow/limited |
| DB | Neon or Supabase | Postgres 15/16 |
| Media | Cloudflare R2 (S3-compatible) or AWS S3 | Mountable from Modal via `CloudBucketMount` |
| Weights cache | **Modal Volume** | Persist Glimmer / tokenizer / HF cache across runs |

---

## 3. Why Modal sustains “heavy” better than Render free

| Need | Render free | Modal |
| --- | --- | --- |
| Multi‑GB model weights | ❌ ~512 MB class pain / ephemeral | ✅ Volumes + image layers |
| GPU inference | ❌ | ✅ A10/L4/A100/… pool |
| Idle cost | Spin-down kills cold demos | Scale-to-zero; warm containers for finals |
| Toolsmith isolation | DIY Docker limits | First-class Sandboxes |
| Hackathon credits | None special | Partner ~$100 (+ Meta API ~$150) |
| Python FastAPI | OK | Native |

Keep containers warm for judging:

- Schedule a tiny ping every few minutes **only Nov 4–9**, or  
- `min_containers=1` on the API / Glimmer function during finals (spend credits deliberately).

---

## 4. Environment variables

```bash
# Meta
MODEL_API_KEY=
META_BASE_URL=https://api.meta.ai/v1
META_OBSERVER_MODEL=muse-spark-1.3
META_PI_MODEL=muse-wonder-1.0
META_IMAGE_MODEL=muse-image-1.0
META_SAM_MODEL=sam-3.1
META_VOICE_MODEL=muse-voice-transcribe-1.0
META_USE_CONTRIBUTOR=false

# App
DATABASE_URL=                 # Neon/Supabase
MEDIA_BUCKET_URL=             # r2:// or s3://
AWS_ACCESS_KEY_ID=            # or R2 equivalents
AWS_SECRET_ACCESS_KEY=
AWS_ENDPOINT_URL=             # R2 endpoint if used
FIXTURE_MODE=false
CORS_ORIGINS=https://hypatia.vercel.app

# Modal / partners
MODAL_TOKEN_ID=
MODAL_TOKEN_SECRET=
BASETEN_API_KEY=              # optional alternate Glimmer host
FIREWORKS_API_KEY=            # optional
```

Web (Vercel) should only need `NEXT_PUBLIC_API_URL` (or same-origin rewrites). Keep `MODEL_API_KEY` on Modal only.

---

## 5. Modal app sketch

```python
# services/api/modal_app.py (sketch)
import modal

app = modal.App("hypatia")
vol = modal.Volume.from_name("hypatia-weights", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements("services/api/requirements.txt")
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("hypatia-secrets")],
    volumes={"/weights": vol},
    timeout=60 * 15,
    memory=4096,          # API brain; bump if needed
    min_containers=0,     # set 1 during finals
)
@modal.asgi_app()
def fastapi_app():
    from hypatia.app import app as api
    return api

@app.function(
    image=image,
    gpu="A10G",           # or "L4" / "A100" once sized
    volumes={"/weights": vol},
    timeout=60 * 30,
    memory=16384,
    scaledown_window=60 * 10,
)
def glimmer_swarm(candidates_request: dict) -> dict:
    ...
```

Toolsmith: spawn `modal.Sandbox` with network off (or allowlist), resource limits, and a unit-test command against recorded frames.

Deploy:

```bash
modal deploy services/api/modal_app.py
modal volume create hypatia-weights   # once
```

---

## 6. Frontend (Vercel)

```bash
cd apps/web && vercel --prod
```

`next.config` rewrite example:

```js
async rewrites() {
  return [{ source: "/api/:path*", destination: "https://<hypatia>--fastapi-app.modal.run/api/:path*" }];
}
```

---

## 7. Media & weights strategy

| Asset | Store | Access |
| --- | --- | --- |
| User uploads / demo MP4s | R2 or S3 | Presigned URL → API; optional Modal `CloudBucketMount` |
| SAM masks / trajectories | R2/S3 or Postgres JSON for small series | |
| Glimmer / HF weights | **Modal Volume** `/weights` | Survives scale-to-zero |
| Demo Meta `file_id`s | Postgres | Warm with `scripts/warm_meta_files.py` |
| Fixtures | Git (JSON) + Volume/R2 for big blobs | `FIXTURE_MODE=true` |

**Never** rely on container local disk for durable state.

---

## 8. When to use AWS instead (or in addition)

Use **AWS pieces** without boiling the ocean:

| Piece | Use now? | Role |
| --- | --- | --- |
| **S3** | ✅ Yes (or R2) | Media bucket — works with Modal mounts |
| **RDS / Aurora** | ❌ Prefer Neon this week | Overkill setup |
| **ECS Fargate** | ❌ | No GPU; slower DX than Modal for Python agents |
| **EC2 g5 / g6** | Only if Modal credits dry / need dedicated box | Always-on Glimmer for finals |
| **SageMaker** | ❌ for hackathon | Heavy ops |
| **CloudFront** | Optional | CDN in front of Vercel/R2 |

**Post-hackathon production shape (if HYPATIA continues):**

```text
CloudFront → ALB → ECS/EKS API  +  SageMaker/EC2 GPU for Glimmer
                → RDS Postgres  +  S3
```

That is a migration *from* Modal, not the day-3 build target.

---

## 9. Cost control (credits week)

1. Meta API: Wonder sparingly; Spark (+ contributor if OK) for volume; cache SAM tracks.  
2. Modal: keep Glimmer cold during build; warm only for recording + judging.  
3. Prefer Meta-hosted `sam-3.1` until open-SAM is proven needed.  
4. R2 free egress to Cloudflare is nice if the UI is on a CF-friendly path; S3 is fine too.  
5. Cap Modal spend; alert at 50% of partner credits.

---

## 10. Demo reliability modes

| Mode | Behavior |
| --- | --- |
| `live` | Meta API + Modal Glimmer |
| `hybrid` | Live Spark/Wonder; cached SAM; Glimmer optional |
| `fixture` | Full offline session replay |

For finals: start **hybrid** with Modal API `min_containers=1`; fall back to **fixture** in &lt;5s.

---

## 11. CI / CD

GitHub Actions:

1. `lint` / `test` (fixture only — no GPU required)  
2. On `main`: `modal deploy` (OIDC or token secret) + `vercel deploy --prebuilt`  
3. Optional: scheduled health check against Vercel `/api/health` proxy  

---

## 12. Launch checklist (submit day)

- [ ] Vercel URL loads; API rewrite hits Modal  
- [ ] `GET /api/health` 200  
- [ ] Pendulum observe→measure &lt; 60s (or hybrid)  
- [ ] Ghost overlay path works  
- [ ] Glimmer path either live **or** documented stub with Spark substitute (honest)  
- [ ] Modal Volume has weights pre-pulled (`modal run … warmup`)  
- [ ] R2/S3 upload works; Postgres migrations applied  
- [ ] Secrets only in Modal Secret + Vercel env  
- [ ] Laptop `docker compose` offline bundle as last resort  
- [ ] README links: live app, video, architecture  

---

## 13. Local docker path

```bash
docker compose up --build
# web :3000  api :8000  postgres :5432
```

Same feature flags (`FIXTURE_MODE`). Local can call Meta API; Glimmer may be stubbed without GPU.

---

## 14. Domain / branding

- Public: `https://hypatia-<team>.vercel.app` (or custom domain)  
- API: Modal `*.modal.run` (hidden behind rewrites)  
- OG image with tagline for viral clip unfurls  

---

## 15. Migration note from earlier Render plan

`render.yaml` is **not** the primary path anymore. If a Render stub remains in the repo, treat it as legacy/optional. New code should assume:

**Vercel + Modal + Neon/Supabase + R2/S3.**
