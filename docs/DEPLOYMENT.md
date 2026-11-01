# Deployment Plan

**Rule from Mitrazzz:** finish the whole product. Do not defer deploy.  
**Priority order (locked):**

1. **Whatever Meta already named for this hackathon**  
2. **AWS** as the next choice if a Meta-named piece cannot cover a need  
3. Nothing else as primary (no Render free, no “decide later”)

---

## 0. What Meta already named

From the official Meta Global AI Developer Hackathon materials:

### A. Meta Model API (required path for hosted Muse + SAM)

| Surface | Model IDs | We use it for |
| --- | --- | --- |
| Inference API | `muse-spark-1.3`, `muse-wonder-1.0`, `muse-image-1.0`, `muse-voice-transcribe-1.0`, `sam-3.1` | Observer, PI, ghost frames, voice, open-vocab measurement |
| Base URL | `https://api.meta.ai/v1` | All hosted calls |
| Auth | `MODEL_API_KEY` | Bearer token |
| Credits | ~$150 per participant | Primary spend |

This is **not optional**. Stage One fails without real Meta Model API / open-weight usage.

### B. Hackathon inference partners (Meta listed these on the event page)

| Partner | What Meta offered | HYPATIA job |
| --- | --- | --- |
| **Modal** | ~$100 credits; open-weight Endpoints; **serverless GPUs**; **sandboxes**; LLM tooling | FastAPI host, Glimmer GPU, Toolsmith sandbox, weight Volumes |
| **Baseten** | ~$100 credits; 2M TPM; Meta open-weights | Alternate / burst Glimmer serving |
| **Fireworks** | ~$100 credits; Meta open-weights + workshop | Alternate open-weight inference |

**Deploy doctrine:** use **Meta Model API + Modal first**, with **Baseten/Fireworks** as open-weight failover.  
**AWS** fills storage / managed DB / production GPU only when a Meta-named tool does not cover it cleanly.

---

## 1. Locked stack

| Layer | Primary (Meta-named) | Secondary (AWS) |
| --- | --- | --- |
| Multimodal brain | Meta Model API | — |
| App API + GPU + sandboxes | **Modal** | ECS/EC2 if Modal unavailable |
| Open-weight Glimmer | Modal GPU **or** Baseten **or** Fireworks | EC2 `g5`/`g6` or SageMaker endpoint |
| Web UI | Modal static/proxy **or** same-origin from Modal | Amplify / S3+CloudFront (AWS) |
| Object storage | Modal Volume (weights/cache) | **AWS S3** (videos, masks, notebooks) |
| Database | Modal Dict/SQLite for ultra-thin demos **or** partner Postgres | **AWS RDS Postgres** |
| Secrets | Modal Secrets | AWS Secrets Manager |
| CI deploy | `modal deploy` from GitHub Actions | Optional dual-deploy to AWS later |

**Public URL strategy:** one URL for judges.

- Preferred: Modal ASGI web endpoint serves API; Next.js can be served from Modal too **or** proxied.  
- If we need a separate frontend host and Meta partners do not fit: **AWS Amplify** or **S3 + CloudFront**.

Render free is **out**.

---

## 2. Topology

```text
                        Judges
                          │
                          ▼
                 Public HTTPS URL
            (Modal web endpoint preferred;
             else AWS CloudFront/Amplify → API)
                          │
                          ▼
              ┌───────────────────────┐
              │  HYPATIA FastAPI      │
              │  on Modal ASGI        │
              └───────────┬───────────┘
                          │
     ┌────────────┬───────┼────────┬──────────────┐
     ▼            ▼       ▼        ▼              ▼
 Meta Model   Modal GPU  Modal   Baseten/     AWS S3
 API          Glimmer    Sandbox Fireworks    (+ RDS if needed)
 Spark/Wonder Volumes    Toolsmith open-wt
 Image/SAM/Voice
```

---

## 3. Why this order (not “AWS first”)

| Concern | Meta-named path | AWS-first |
| --- | --- | --- |
| Judging “use Meta tooling” | Direct, obvious | Easy to look like a generic AWS app |
| Partner credits | Modal / Baseten / Fireworks already granted | Pay out of pocket / Free Tier limits |
| GPU + sandbox in one product | Modal | EC2 + separate sandbox story |
| Heavy weights | Modal Volumes | S3 + big GPU instance ops |
| Deadline | `modal deploy` in minutes | VPC/IAM/ALB/ECS days |

AWS is **priority #2**, not abandoned: S3 for media is expected; full AWS compute is the backup if Modal/Baseten/Fireworks cannot run.

---

## 4. Environment variables

```bash
# === Meta Model API (required) ===
MODEL_API_KEY=
META_BASE_URL=https://api.meta.ai/v1
META_OBSERVER_MODEL=muse-spark-1.3
META_PI_MODEL=muse-wonder-1.0
META_IMAGE_MODEL=muse-image-1.0
META_SAM_MODEL=sam-3.1
META_VOICE_MODEL=muse-voice-transcribe-1.0
META_USE_CONTRIBUTOR=false

# === Meta partners ===
MODAL_TOKEN_ID=
MODAL_TOKEN_SECRET=
BASETEN_API_KEY=
FIREWORKS_API_KEY=
GLIMMER_PROVIDER=modal   # modal | baseten | fireworks | stub

# === AWS (priority #2 — storage / fallback compute) ===
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET=hypatia-media
DATABASE_URL=            # postgres; Neon OK short-term, RDS for AWS path
FIXTURE_MODE=false
CORS_ORIGINS=*
```

---

## 5. Modal deploy (primary)

```bash
# one-time
modal token set --token-id "$MODAL_TOKEN_ID" --token-secret "$MODAL_TOKEN_SECRET"
modal volume create hypatia-weights
modal secret create hypatia-secrets MODEL_API_KEY=... AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... S3_BUCKET=...

# ship
modal deploy services/api/modal_app.py
```

App sketch lives in `services/api/modal_app.py`:

- `@modal.asgi_app()` → FastAPI  
- `@app.function(gpu=...)` → Glimmer swarm  
- `modal.Sandbox` → Toolsmith  
- `modal.Volume` → `/weights`  
- Optional `CloudBucketMount` → AWS S3 for videos  

Warm for finals: set `min_containers=1` on API + Glimmer **Nov 4–9 only**.

---

## 6. Baseten / Fireworks (open-weight failover)

If Modal GPU quota/credits fail:

1. Deploy Glimmer (or Spark Open) on **Baseten** or **Fireworks** using partner credits.  
2. Set `GLIMMER_PROVIDER=baseten` or `fireworks`.  
3. Keep orchestration on Modal CPU ASGI **or** fall through to AWS.

Interface: `HypothesisSwarm` — one adapter per provider. CI uses `stub`.

---

## 7. AWS fallback (priority #2)

Use when Meta partners cannot host a layer:

| Need | AWS service |
| --- | --- |
| Video / mask / notebook blobs | **S3** (use even in Modal-primary mode) |
| Managed Postgres | **RDS** |
| Always-on API if Modal outage | **ECS Fargate** (CPU) behind ALB |
| Dedicated Glimmer GPU | **EC2 g5/g6** or **SageMaker Real-time** |
| Frontend | **Amplify** or **S3 + CloudFront** |
| Secrets | **Secrets Manager** |

Terraform/CDK can wait until Modal path is green; keep an `infra/aws/` folder once the API contract is stable.

**Important:** Fargate has **no GPU**. GPU on AWS = EC2/SageMaker, not Fargate.

---

## 8. Local / CI

```bash
docker compose up --build
# web :3000  api :8000  (minio optional for S3-compatible local)
```

- `FIXTURE_MODE=true` → full demo without burning Meta credits  
- Live smoke: `python scripts/smoke_meta_api.py`  

CI: lint + fixture tests on every PR; `modal deploy` on `main`.

---

## 9. Demo reliability

| Mode | Behavior |
| --- | --- |
| `live` | Meta Model API + Modal/Baseten/Fireworks Glimmer |
| `hybrid` | Live Spark/Wonder; cached SAM tracks; swarm optional |
| `fixture` | Offline golden session (finals insurance) |

---

## 10. Launch checklist

- [ ] `MODEL_API_KEY` works from India (Spark + SAM smoke)  
- [ ] `modal deploy` URL healthy  
- [ ] S3 or local MinIO upload path works  
- [ ] Pendulum E2E &lt; 60s live or hybrid  
- [ ] Ghost path works (Image or geometric fallback)  
- [ ] Glimmer provider documented and callable **or** honest Spark substitute  
- [ ] Fixture mode switch verified  
- [ ] README links: live URL, demo video, Meta models list  
- [ ] AWS creds present only as storage/fallback — not required for Meta-only happy path  

---

## 11. Explicit non-goals

- Render free as primary  
- “Deploy later”  
- AWS-only architecture that hides Meta partners Meta already funded us to use  
