#!/usr/bin/env bash
# Creates HYPATIA milestones, labels, and detailed issues. Idempotent-ish: skips existing labels/milestones errors.
set -euo pipefail
REPO="mitra9917/HYPATIA"

create_label() {
  gh label create "$1" --color "$2" --description "$3" --repo "$REPO" 2>/dev/null || true
}

create_milestone() {
  local title="$1" desc="$2" due="$3"
  gh api "repos/${REPO}/milestones" -f title="$title" -f description="$desc" -f due_on="$due" 2>/dev/null || true
}

issue() {
  local title="$1" milestone="$2" labels="$3"
  shift 3
  gh issue create --repo "$REPO" --title "$title" --milestone "$milestone" --label "$labels" --body "$1"
}

echo "Creating labels..."
for pair in \
  "phase/0|0E8A16|Planning and integration spine" \
  "phase/1|1D76DB|Perception vertical slice" \
  "phase/2|5319E7|Hypothesis loop and first law" \
  "phase/3|B60205|Ghost, experiment, voice" \
  "phase/4|D93F0B|Deploy, evals, submission" \
  "seat/agent|FBCA04|Agent orchestration / API" \
  "seat/vision|F9D0C4|SAM, calibration, ghost vision" \
  "seat/science|C5DEF5|PySR, scoring, VERITAS" \
  "seat/product|BFDADC|UI, demo, deploy surface" \
  "meta/spark|0075CA|Muse Spark API" \
  "meta/wonder|0052CC|Muse Wonder API" \
  "meta/sam|006B75|SAM 3.1 API" \
  "meta/image|8250DF|Muse Image API" \
  "meta/glimmer|6F42C1|Open-weight Glimmer" \
  "meta/voice|E99695|Muse Voice Transcribe" \
  "meta/code|24292F|Muse Code process evidence" \
  "integration-human|D4C5F9|Human-only: keys, dashboards, billing" \
  "blocker|B60205|Blocks downstream coding" \
  "demo-critical|FF0000|Demo script beat — do not cut"; do
  IFS='|' read -r name color desc <<< "$pair"
  create_label "$name" "$color" "$desc"
done

echo "Creating milestones..."
create_milestone "M0 — Docs & integration spine" "Phase 0: docs agreed + YOU configure Meta/partner accounts before live model work." "2026-11-01T18:30:00Z"
create_milestone "M1 — Perception E2E" "Upload/webcam → Spark SceneBrief → SAM tracks → trajectory chart in UI." "2026-11-01T23:59:00Z"
create_milestone "M2 — First law" "Glimmer swarm + Wonder PI + PySR + held-out gate + hypothesis UI." "2026-11-02T23:59:00Z"
create_milestone "M3 — Ghost & experiment" "Muse Image ghost + SAM audit + experiment designer + voice loop." "2026-11-03T23:59:00Z"
create_milestone "M4 — Deploy, evals, submit" "Modal/Vercel public URL, evals table, 3:00 video, submission form." "2026-11-04T18:00:00Z"

M0="M0 — Docs & integration spine"
M1="M1 — Perception E2E"
M2="M2 — First law"
M3="M3 — Ghost & experiment"
M4="M4 — Deploy, evals, submit"

echo "Creating issues (this may take a minute)..."

issue "[INTEGRATION] Meta Model API key + dev.meta.ai access (BLOCKER)" "$M0" "integration-human,blocker,meta/spark,meta/wonder,meta/sam,meta/image,meta/voice,phase/0" "$(cat <<'EOF'
## Why this exists
Stage One **fails** without real Meta Model API usage. No coding on live Spark/SAM/Wonder/Image/Voice until this is done.

## What YOU must do (Mitrazzz)
1. Log in at [dev.meta.ai](https://dev.meta.ai) with the **same account** you used for hackathon acceptance.
2. Open **API keys** / Model API section and create a key → copy to local `.env` as `MODEL_API_KEY=` (never commit).
3. Confirm base URL in `.env`: `META_BASE_URL=https://api.meta.ai/v1`
4. Leave model IDs as in `.env.example` unless docs say otherwise:
   - `META_OBSERVER_MODEL=muse-spark-1.3`
   - `META_PI_MODEL=muse-wonder-1.0`
   - `META_IMAGE_MODEL=muse-image-1.0`
   - `META_SAM_MODEL=sam-3.1`
   - `META_VOICE_MODEL=muse-voice-transcribe-1.0`
5. Run from repo root:
   ```bash
   cp .env.example .env   # if not done
   # fill MODEL_API_KEY
   pip install -r services/api/requirements.txt
   python scripts/smoke_meta_api.py
   ```
6. **Contributor mode (optional, cost):** set `META_USE_CONTRIBUTOR=true` only for non-sensitive test loops; keep Standard for anything you would not want in contributor training data (see Official Rules / Meta policy).

## When to do this
**Before** issue P1.2 (Meta client) and **before** any PR that calls live Meta endpoints.

## Definition of done
- [ ] `smoke_meta_api.py` passes or fails with a clear, non-401 error you can paste in Discord OH
- [ ] `.env` is gitignored; `.env.example` has no secrets
- [ ] Comment on this issue: "smoke OK" + date

## References
- `docs/HACKATHON_BRIEF.md` §5
- `docs/META_TOOLING.md`
EOF
)"

issue "[INTEGRATION] Modal account + tokens for API deploy, GPU, sandboxes" "$M0" "integration-human,blocker,phase/0" "$(cat <<'EOF'
## Why
Hackathon partners: **Modal** (~$100 credits) for FastAPI ASGI host, GPU (Glimmer), Toolsmith sandboxes, weight Volumes.

## What YOU must do
1. Sign up / log in at [modal.com](https://modal.com) with hackathon-linked email if required for credits.
2. Install CLI: `pip install modal` then `modal setup` (browser auth).
3. Create tokens at Modal dashboard → copy to `.env`:
   - `MODAL_TOKEN_ID=`
   - `MODAL_TOKEN_SECRET=`
4. From repo: `modal deploy services/api/modal_app.py` (after P4.6 code is ready; dry-run `modal token set` now to verify auth).

## When
- **Now:** verify auth works.
- **Phase 4:** production deploy + warm containers.
- **Phase 2:** if running Glimmer on Modal GPU instead of stub.

## DoD
- [ ] `modal profile current` shows your workspace
- [ ] Comment: workspace name + "tokens in .env only"
EOF
)"

issue "[INTEGRATION] Open-weight Glimmer provider (Modal GPU / Baseten / Fireworks)" "$M0" "integration-human,meta/glimmer,phase/0,phase/2" "$(cat <<'EOF'
## Why
Hackathon requires **open-weight** usage (Muse Glimmer). API-only Spark is not enough for the 25% tooling story.

## What YOU must do (pick one primary path)
### Option A — Modal GPU (preferred, matches `docs/DEPLOYMENT.md`)
1. Ensure Modal integration issue is done.
2. Set `GLIMMER_PROVIDER=modal` (when implemented) or follow P2.2 issue for env var name.
3. Accept GPU spend inside Modal credits.

### Option B — Baseten
1. Apply/use hackathon Baseten credits if you received them.
2. Deploy Muse Glimmer endpoint per Baseten + Meta workshop docs.
3. Set `BASETEN_API_KEY=` and wire URL in P2.2.

### Option C — Fireworks
1. Set `FIREWORKS_API_KEY=` from Fireworks console.
2. Point Glimmer adapter at Fireworks-hosted open weights.

### Until live endpoint exists
Keep `GLIMMER_PROVIDER=stub` in `.env` for CI/fixtures only — **must switch before demo video**.

## When
Before closing **M2 — First law** milestone.

## DoD
- [ ] At least one real Glimmer inference call logged (model, latency) OR documented partner blocker + OH ticket
EOF
)"

issue "[INTEGRATION] Postgres (Neon/Supabase) + optional S3/R2 for media" "$M0" "integration-human,phase/0,phase/4" "$(cat <<'EOF'
## Why
Durable sessions, laws, notebooks — not ephemeral Modal disk alone (`AGENTS.md` non-negotiable #7).

## What YOU must do
1. Create a **free Postgres** (Neon or Supabase hackathon tier).
2. Copy connection string to `.env`: `DATABASE_URL=postgresql://...`
3. For large videos/masks (if not only Meta Files API):
   - **AWS:** create S3 bucket in `ap-south-1` (or your region), set `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` in `.env`
   - Or Cloudflare R2 (S3-compatible) if you prefer

## When
- **Before** P1.6 session persistence beyond in-memory store.
- **Before** public deploy (M4).

## DoD
- [ ] `DATABASE_URL` works from local API (`docker compose up` or direct)
- [ ] Comment which provider (Neon/Supabase/RDS)
EOF
)"

issue "[INTEGRATION] Vercel project for Next.js lab UI" "$M0" "integration-human,seat/product,phase/0,phase/4" "$(cat <<'EOF'
## Why
`AGENTS.md` default: **Vercel (web) + Modal (API)**. Judges need one stable demo URL.

## What YOU must do
1. Import GitHub repo `mitra9917/HYPATIA` in [Vercel](https://vercel.com) — root directory **`apps/web`**.
2. Set environment variables in Vercel project settings:
   - `API_ORIGIN` = your Modal ASGI public URL (after deploy)
   - Any `NEXT_PUBLIC_*` vars the web app requires (see P1.7 / P4.6)
3. Enable preview deployments on PRs; production branch `main`.

## When
After first working local UI (P1.7); **required** before submission (M4).

## DoD
- [ ] Preview URL loads lab UI
- [ ] Production URL listed in README (P4.9)
EOF
)"

issue "[INTEGRATION] Muse Code — process evidence for judges" "$M0" "integration-human,meta/code,phase/0,phase/4" "$(cat <<'EOF'
## Why
Hackathon stack lists **Muse Code** as the coding agent. Judges reward authentic "built with Meta" process.

## What YOU must do
1. Use Muse Code (or document parallel use) for at least one vertical slice PR.
2. Record **10–15s B-roll** of Muse Code committing/running tests (no secrets on screen).
3. Add clip to demo folder or unlisted drive; link in README "Built during hackathon" section.

## When
During Phases 1–3 coding; finalize before **P4.8 demo video**.

## DoD
- [ ] B-roll file linked in issue comment
- [ ] README mentions Muse Code in tooling table (`docs/META_TOOLING.md` §6)
EOF
)"

issue "P0.11 — Verify docs spine + close planning milestone" "$M0" "phase/0,seat/product" "$(cat <<'EOF'
## Context
Phase 0 docs should already exist under `docs/` (see `docs/INDEX.md`).

## Tasks
- [ ] Read order: HACKATHON_BRIEF → PRODUCT → ARCHITECTURE → META_TOOLING → BUILD_PLAN
- [ ] Confirm theme: **Push the Frontier**; track: **Indie**
- [ ] Mark integration issues complete as YOU finish each setup
- [ ] Attach screenshot of repo docs tree in comment

## DoD
All `[INTEGRATION]` issues either closed or have explicit blocker + OH plan.
EOF
)"

issue "P1.1 — Monorepo scaffold hardening (api + web + compose)" "$M1" "phase/1,seat/product,demo-critical" "$(cat <<'EOF'
## Goal
Reliable local full stack for every developer/agent.

## Scope
- `docker compose up` → Postgres + API + web (or documented hybrid: API local, web local)
- `/api/health` returns model router info + `fixture_mode`
- `.env.example` documents every Meta + partner var

## Files
- `docker-compose.yml`, `services/api/`, `apps/web/`, `scripts/run_api_local.sh`

## Tests
- CI or local: import `hypatia` package; health curl

## DoD
- [ ] README quickstart ≤5 commands
- [ ] Demo note: show health JSON in 10s

## Depends
Integration: Meta key optional if `FIXTURE_MODE=true`
EOF
)"

issue "P1.2 — Meta Model API client (Responses + Files + logging)" "$M1" "phase/1,seat/agent,meta/spark,meta/sam,blocker,demo-critical" "$(cat <<'EOF'
## Goal
Single `ModelRouter` / `meta_client` for all hosted Meta calls with structured logging (`model`, tokens/frames, `latency_ms`, `session_id`).

## Scope
- Bearer auth from `MODEL_API_KEY`
- Responses API default; JSON schema helper
- Files API upload for video reuse (`file_id`)
- Contributor flag routing when `META_USE_CONTRIBUTOR=true`

## Meta models touched
Spark, SAM, Wonder (stub call in smoke), Image (optional in smoke), Voice (optional)

## Tests
- `scripts/smoke_meta_api.py` with opt-in live flag
- Fixture path when no key

## DoD
- [ ] No raw keys in logs
- [ ] Document env vars in module docstring

## Depends
**YOU:** `[INTEGRATION] Meta Model API key` closed
EOF
)"

issue "P1.3 — Observer agent (Spark video → SceneBrief JSON)" "$M1" "phase/1,seat/agent,meta/spark,demo-critical" "$(cat <<'EOF'
## Goal
Given pendulum (or generic) clip, produce `SceneBrief`: objects, candidate variables, **`sam_prompts[]`**, suggested domain.

## Contract
See `docs/ARCHITECTURE.md` §4 step OBSERVE and `docs/META_TOOLING.md` §3.1.

## Implementation
- Prompt + JSON schema validation
- Save fixture under `data/fixtures/observer_<scene>.json`
- Wire `POST /api/sessions/{id}/observe`

## DoD
- [ ] Fixture replay works with `FIXTURE_MODE=true`
- [ ] Live call uses `muse-spark-1.3` + video `file_id`
- [ ] Demo: print SceneBrief in UI or API response

## Depends
P1.2
EOF
)"

issue "P1.4 — SAM 3.1 video measurer + meta_sam_parser decode" "$M1" "phase/1,seat/vision,meta/sam,demo-critical" "$(cat <<'EOF'
## Goal
For each `sam_prompt`, run SAM 3.1 on video → stable track IDs, per-frame masks/boxes.

## Contract
`docs/META_TOOLING.md` §3.2 — stream when possible; decode with `meta_sam_parser`.

## Scope
- Upload once, reuse `file_id`
- Cache tracks to `data/fixtures/` keyed by session + prompt
- Cost guard: downsample to 10–15 fps scientific clips

## DoD
- [ ] Masks available to frontend as overlay payload or URLs
- [ ] Log frames billed estimate

## Depends
P1.2, P1.3 (`sam_prompts`)
EOF
)"

issue "P1.5 — Calibration + SI trajectories (A4 / coin + OpenCV)" "$M1" "phase/1,seat/vision,seat/science,demo-critical" "$(cat <<'EOF'
## Goal
Convert pixel tracks → metres, radians, seconds with uncertainty notes.

## Scope
- Detect scale object (A4 210×297 mm or ₹10 coin) via SAM prompt or heuristics
- Extract angle (PCA), length, position time series
- Unit tests for scale math (no Meta)

## DoD
- [ ] CSV + chart-ready JSON on session
- [ ] Pendulum angle series monotonic with period visible

## Depends
P1.4
EOF
)"

issue "P1.6 — Session API + Postgres persistence + SSE progress" "$M1" "phase/1,seat/agent,demo-critical" "$(cat <<'EOF'
## Goal
Full session lifecycle with live UI progress.

## Endpoints
`POST /api/sessions`, `GET /api/sessions/{id}`, `GET /api/sessions/{id}/events` (SSE)

## Data model
Minimal tables per `docs/ARCHITECTURE.md` §5: Session, Observation, Track

## DoD
- [ ] SSE emits stage: observe → measure → …
- [ ] Survives API restart when `DATABASE_URL` set

## Depends
P1.1, **INTEGRATION Postgres**
EOF
)"

issue "P1.7 — Lab UI: upload/webcam, mask overlay, trajectory chart" "$M1" "phase/1,seat/product,demo-critical" "$(cat <<'EOF'
## Goal
Browser upload runs observe→measure; user sees SAM overlay + time series chart.

## Scope
- `apps/web`: session create, file picker, poll/SSE
- `GhostCanvas` or new overlay component for masks
- Chart for angle vs time (pendulum)

## DoD
- [ ] 30s GIF attached to PR/issue
- [ ] Works in fixture mode for judges offline

## Depends
P1.3–P1.6
EOF
)"

issue "P1.8 — Test video corpus + SOURCES.md (rights-safe)" "$M1" "phase/1,seat/science" "$(cat <<'EOF'
## Goal
≥8 desk clips: pendulum, ramp, free fall, cell timelapse placeholder, fake AI physics clip.

## DoD
- [ ] `data/videos/SOURCES.md` lists license/ownership per clip
- [ ] Large files external link OK per `docs/REPO_STRUCTURE.md`

## No Meta required
EOF
)"

issue "P1.9 — Fixture recorder + replay mode banner" "$M1" "phase/1,seat/agent,demo-critical" "$(cat <<'EOF'
## Goal
Record live Meta responses to fixtures; UI banner when `FIXTURE_MODE=true` ("replay mode").

## DoD
- [ ] One-command record script for observer + SAM slice
- [ ] Demo-critical path never 500s without key

## Depends
P1.3–P1.5
EOF
)"

issue "P2.1 — Equation DSL + PySR / SciPy symbolic fitter" "$M2" "phase/2,seat/science,demo-critical" "$(cat <<'EOF'
## Goal
Fit candidate laws on train window; output params + LaTeX.

## Scope
- Pendulum: \(T=2\pi\sqrt{L/g}\), small-angle \(\theta(t)\), etc.
- No LLM in acceptance — maths only

## Tests
Unit tests on synthetic trajectories

## DoD
- [ ] Fits recover g within tolerance on fixture data
EOF
)"

issue "P2.2 — Glimmer swarm adapter (theorist batch + CPU stub)" "$M2" "phase/2,seat/agent,meta/glimmer,demo-critical" "$(cat <<'EOF'
## Goal
N rival functional forms from Glimmer (or stub in CI); pre-screen before PySR.

## Env
`GLIMMER_PROVIDER`, Modal/Baseten/Fireworks keys

## DoD
- [ ] ≥3 rivals generated for pendulum session
- [ ] Live provider switch documented in README

## Depends
**INTEGRATION Glimmer** for live; stub OK for early dev
EOF
)"

issue "P2.3 — Wonder PI orchestration (plan → measure → hypothesize)" "$M2" "phase/2,seat/agent,meta/wonder,demo-critical" "$(cat <<'EOF'
## Goal
PI plans campaign; delegates to Spark/Glimmer/PySR tools; uses `previous_response_id` continuity.

## Tools (structured)
spawn_theorist, run_pysr, library_search (stub OK initially)

## DoD
- [ ] `POST /api/sessions/{id}/hypothesize` returns ranked hypotheses
- [ ] Wonder called once per major phase, not per keystroke

## Depends
P2.1, P2.2, P1.5
EOF
)"

issue "P2.4 — Held-out scoring gate + bootstrap confidence intervals" "$M2" "phase/2,seat/science,demo-critical" "$(cat <<'EOF'
## Goal
LLM proposes, maths decides — block acceptance without held-out win.

## Gates
See `docs/ARCHITECTURE.md` §9

## DoD
- [ ] Unit tests for gate edge cases
- [ ] UI shows train vs held-out scores
EOF
)"

issue "P2.5 — UI hypothesis cards + rival comparison" "$M2" "phase/2,seat/product,demo-critical" "$(cat <<'EOF'
## Goal
2–5 cards with LaTeX/form, scores, status (leading/eliminated).

## DoD
- [ ] Demo beat: \(T=2\pi\sqrt{L/g}\), \(g \approx 9.7 \pm 0.4\)
EOF
)"

issue "P2.6 — Lab notebook markdown export" "$M2" "phase/2,seat/product" "$(cat <<'EOF'
## Goal
Export law, constants ± err, video ref, CSV link, models used.

## DoD
- [ ] `GET` or download endpoint; sample notebook in `demo/`
EOF
)"

issue "P2.7 — Eval harness v0 (≥5 clips metrics)" "$M2" "phase/2,seat/science" "$(cat <<'EOF'
## Goal
Script under `evals/` reporting law recovery rate, SAM cost, latency.

## See
`docs/EVALS.md`

## DoD
- [ ] Table output suitable for README (P4.7)
EOF
)"

issue "P3.1 — Predictor (kinematic / ODE forward simulation)" "$M3" "phase/3,seat/science,demo-critical" "$(cat <<'EOF'
## Goal
From candidate law → predicted state at t+Δ for ghost pipeline.

## DoD
- [ ] Matches ground truth on fixture pendulum within tolerance
EOF
)"

issue "P3.2 — Muse Image ghost pipeline + mask hints" "$M3" "phase/3,seat/vision,meta/image,demo-critical" "$(cat <<'EOF'
## Goal
Edit current frame toward predicted state (`muse-image-1.0`).

## Contract
`docs/META_TOOLING.md` §3.4

## DoD
- [ ] `POST /api/sessions/{id}/imagine` returns ghost frame URI
- [ ] Budget: log image count (~$0.01 each)

## Depends
P3.1, Meta key
EOF
)"

issue "P3.3 — SAM imagination audit (predicted vs real frame)" "$M3" "phase/3,seat/vision,meta/sam,demo-critical" "$(cat <<'EOF'
## Goal
Segment object in ghost vs real next frame → IoU / centroid error → score meter in UI.

## Money line
"SAM grades Muse Image" (`docs/META_TOOLING.md` §2)

## DoD
- [ ] ImaginationAudit row persisted
EOF
)"

issue "P3.4 — Geometric ghost fallback renderer" "$M3" "phase/3,seat/vision,demo-critical" "$(cat <<'EOF'
## Goal
If Muse Image fails, draw kinematic overlay; still run SAM audit on composite.

## DoD
- [ ] Feature flag or auto-fallback documented in `docs/RISKS.md` runbook
EOF
)"

issue "P3.5 — Experiment Designer (information gain over rivals)" "$M3" "phase/3,seat/agent,meta/wonder" "$(cat <<'EOF'
## Goal
`NextTest` JSON: instruction + expected outcomes per theory.

## Endpoint
`POST /api/sessions/{id}/experiment/propose`

## DoD
- [ ] Pendulum: suggests doubling string length with numeric predictions
EOF
)"

issue "P3.6 — Human-in-the-loop experiment UI + result ingestion" "$M3" "phase/3,seat/product,demo-critical" "$(cat <<'EOF'
## Goal
User marks experiment done; upload new clip or confirm; re-measure → update posteriors.

## Endpoint
`POST /api/sessions/{id}/experiment/result`

## DoD
- [ ] Demo script beat 0:45–1:15 covered
EOF
)"

issue "P3.7 — Voice loop (Muse Voice Transcribe → PI reply)" "$M3" "phase/3,seat/product,meta/voice,demo-critical" "$(cat <<'EOF'
## Goal
Hands-free: "What if heavier bob?" while adjusting apparatus.

## Implementation
- File ASR for MVP; stretch: realtime WS `wss://api.meta.ai/v1/asr/realtime`
- `POST /api/voice/turn`

## DoD
- [ ] Mic button in UI; transcript + PI text visible

## Depends
Meta key, P2.3
EOF
)"

issue "P3.8 — Hybrid fixture/live mode switch + ops banner" "$M3" "phase/3,seat/agent" "$(cat <<'EOF'
## Goal
Env + runtime toggle; cost dashboard snippet in logs.

## DoD
- [ ] Operator can flip live demo → fixtures without redeploy (env or admin flag)
EOF
)"

issue "P4.1 — Toolsmith sandbox (Modal) + unit test on frames" "$M4" "phase/4,seat/agent,meta/wonder" "$(cat <<'EOF'
## Goal
Wonder writes measurement code; runs in Modal sandbox with no host network; promotes to Tool library.

## DoD
- [ ] One promoted tool from pendulum or cell domain
- [ ] Modal integration working

## Depends
INTEGRATION Modal
EOF
)"

issue "P4.2 — Law + tool library persistence + API" "$M4" "phase/4,seat/agent,demo-critical" "$(cat <<'EOF'
## Goal
`GET /api/library/laws`; cross-session speedup chart (stretch).

## DoD
- [ ] Second pendulum session hits library
EOF
)"

issue "P4.3 — Cell time-lapse domain (reuse engine)" "$M4" "phase/4,seat/science,seat/vision,meta/spark" "$(cat <<'EOF'
## Goal
Observer → logistic growth / doubling time; optional Toolsmith cell counter.

## DoD
- [ ] Demo clip in notebook export
EOF
)"

issue "P4.4 — VERITAS module (AI fall clip physics break)" "$M4" "phase/4,seat/science,meta/spark,meta/sam" "$(cat <<'EOF'
## Goal
Detect non-physical acceleration / momentum break with frame evidence.

## DoD
- [ ] Verdict card on fake physics video (P1.8 corpus)
EOF
)"

issue "P4.5 — [STRETCH] Wonder computer use vs PhET pendulum" "$M4" "phase/4,seat/agent,meta/wonder" "$(cat <<'EOF'
## Goal
Autonomous browser: change length, release, read period.

## Cut last
Per BUILD_PLAN — drop before ghost or held-out gates.

## Ref
https://dev.meta.ai/docs/computer-use
EOF
)"

issue "P4.6 — Production deploy: Modal API + Vercel web + health/warm" "$M4" "phase/4,seat/product,demo-critical,blocker" "$(cat <<'EOF'
## Goal
Public HTTPS demo stable through judging window.

## Tasks
- `modal deploy services/api/modal_app.py` — bind `0.0.0.0`, `/api/health`
- Vercel `apps/web` with `API_ORIGIN` → Modal URL
- CORS `CORS_ORIGINS` includes Vercel domain
- Optional: warm ping cron

## DoD
- [ ] README demo URL
- [ ] Health green from external curl

## Depends
INTEGRATION Modal + Vercel + Postgres/S3 as used
EOF
)"

issue "P4.7 — Evals table + Meta tooling evidence in README" "$M4" "phase/4,seat/science,meta/spark,meta/wonder,meta/sam,meta/image,meta/glimmer,meta/voice" "$(cat <<'EOF'
## Goal
Publish tables from `docs/META_TOOLING.md` §5 and `docs/EVALS.md` with real numbers.

## DoD
- [ ] Every Meta model has file path + demo timestamp
EOF
)"

issue "P4.8 — Record and edit 3:00 demo video" "$M4" "phase/4,seat/product,demo-critical,blocker" "$(cat <<'EOF'
## Goal
Primary judging artifact — genuinely cool, all beats from `demo/DEMO_SCRIPT.md`.

## Checklist
- [ ] Pendulum law card
- [ ] Ghost overlay 8+ seconds
- [ ] Experiment ask
- [ ] Voice turn
- [ ] Cell or VERITAS beat
- [ ] Muse Code B-roll in credits

## DoD
Unlisted/public URL in submission form
EOF
)"

issue "P4.9 — Submission package (form, links, open source checklist)" "$M4" "phase/4,seat/product,blocker" "$(cat <<'EOF'
## Goal
Submit before **Nov 4, 9:00 PM ET** (Nov 5 7:30 AM IST) with buffer.

## Include
- Public GitHub
- Deploy URL
- Video link
- Theme: Push the Frontier; Track: Indie
- Explicit Meta models list
- "Built during hackathon" section

## See
`docs/HACKATHON_BRIEF.md` §7
EOF
)"

issue "P4.10 — Public social clip + repo polish" "$M4" "phase/4,seat/product" "$(cat <<'EOF'
## Goal
Optional viral/bonus pool — 30–60s clip for X/LinkedIn.

## DoD
- [ ] Link in README; tag #MetaAIHackathon per event guidance
EOF
)"

echo "Done. List issues:"
gh issue list --repo "$REPO" --limit 100
