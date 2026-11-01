# AGENTS.md — Conventions for HYPATIA builders

This file is for humans and coding agents working in this repo during the Meta Global AI Developer Hackathon.

## Mission

Build **HYPATIA**: a camera that does science — observe → measure → hypothesize → imagine → audit → experiment → learn — using Meta Model API + open weights as load-bearing components.

Read `docs/INDEX.md` before large changes.

## Non-negotiables

1. **Public, new work** — assume the repo is public; only commit what we have rights to.
2. **Meta tools must be essential** — do not add a model call for checkbox theater.
3. **LLM proposes, maths decides** — never accept a law without held-out scoring.
4. **Demo reliability** — every Meta-facing path needs a fixture fallback.
5. **Secrets stay out of git** — `.env` only; document keys in `.env.example`.
6. **Render bind** — HTTP servers listen on `0.0.0.0:$PORT`.
7. **Ephemeral disk** — do not treat local FS as durable storage in production.

## Stack defaults

| Layer | Choice |
| --- | --- |
| Frontend | Next.js (App Router) + TypeScript |
| Backend | FastAPI + uvicorn |
| DB | Postgres |
| Meta API | Responses API @ `https://api.meta.ai/v1` |
| SAM decode | `meta_sam_parser` (Python) / `@meta-sam/parser` (TS) |
| Science | NumPy, SciPy, OpenCV, PySR |
| Deploy | Render Blueprint + optional Modal sandboxes |

## Model routing

Use a single `ModelRouter` / env-configured IDs:

- Observer / narration / cheap tools → `muse-spark-1.3` (or contributor variant when policy OK)
- PI / Toolsmith / Experiment Designer / computer use → `muse-wonder-1.0`
- Ghost frames → `muse-image-1.0`
- Masks / tracks / audits → `sam-3.1`
- Voice → `muse-voice-transcribe-1.0`
- Hypothesis swarm → Muse Glimmer via partner/local (stub allowed in CI)

Log `model`, `tokens`/`frames`, `latency_ms`, `session_id` for every call.

## Code style

- Prefer small modules with clear agent boundaries (`observer`, `measurer`, `pi`, …).
- Structured outputs with JSON schemas for agent→API contracts.
- No silent `except:`; fail into fixture mode or user-visible error.
- Frontend: one job per section; brand **HYPATIA** is the hero signal on marketing surfaces.
- Do not add drive-by refactors unrelated to the issue.

## Testing

- Unit-test scoring gates and calibration math without Meta.
- Contract-test routes with fixture payloads.
- Live Meta smoke only via `scripts/smoke_meta_api.py` with explicit opt-in.

## PR hygiene

- Branch: `cursor/<descriptive>-db99`
- One milestone concern per PR when possible
- Update docs if behavior or architecture changes
- Mention which Meta models the PR touches in the PR body

## Demo-critical paths (protect these)

1. Pendulum session → law card  
2. Ghost overlay  
3. Experiment recommendation  
4. Health endpoint + deploy  
5. Fixture replay mode  

Changes that risk these need extra review and a recorded GIF.
