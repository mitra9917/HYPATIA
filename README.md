# HYPATIA

[![CI](https://github.com/mitra9917/HYPATIA/actions/workflows/ci.yml/badge.svg)](https://github.com/mitra9917/HYPATIA/actions/workflows/ci.yml)

**The camera that does science.**

Point any camera at anything that moves. HYPATIA finds the law behind it, proves the law by predicting the future, then tells you which experiment to run next.

> We gave Meta's models a camera and the scientific method. It rediscovered Galileo on my desk in 90 seconds.

Built for the **[Meta Global AI Developer Hackathon](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)** — **Indie track** · **Push the Frontier**.

| | |
| --- | --- |
| **Hackathon alignment (judges / parsers)** | [`docs/HACKATHON_ALIGNMENT.md`](docs/HACKATHON_ALIGNMENT.md) · [`meta_evidence.json`](meta_evidence.json) |
| **Submission pack** | [`docs/SUBMISSION_PACK.md`](docs/SUBMISSION_PACK.md) |
| Status | Full-stack E2E (fixture + Meta live hooks) · playbooks through **#62** |
| Deadline | **Nov 4, 2026, 9:00 PM ET** / **Nov 5, 7:30 AM IST** |
| Deploy priority | **Meta Model API → Modal / Baseten / Fireworks → AWS** |
| Live demo URL | _Set after `modal deploy` — see [`docs/PRODUCTION_DEPLOY_CHECKLIST.md`](docs/PRODUCTION_DEPLOY_CHECKLIST.md)_ |
| Demo video | _~3 min — script [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md)_ |

---

## Quick start (local)

```bash
cp .env.example .env          # optional; fixture mode needs no Meta key
./scripts/run_api_local.sh    # terminal 1 — API on :8000
cd apps/web && npm ci && npm run dev   # terminal 2 — UI on :3000
./scripts/smoke_health.sh     # fast /api/health (Meta ping optional: …/health meta)
./scripts/smoke_playbook_52_57.sh   # live smoke for phase-4 API routes
bash scripts/verify_playbook_58_62.sh  # evals + cost report + submission docs
```

**Docker full stack:** `docker compose up --build` → http://localhost:3000

Set `apps/web/.env.local` → `NEXT_PUBLIC_API_ORIGIN=http://127.0.0.1:8000` so the lab UI talks to the API directly (avoids Next proxy timeouts on long runs).

---

## Eval results (fixture — CI-safe)

| Clip | True law | Recovered (fixture) | Key const | Ghost MAE (m) |
| --- | --- | --- | --- | --- |
| pendulum_desk_fixture | \(T=2\pi\sqrt{L/g}\) | same | g ≈ 9.8 ± 0.4 m/s² | 0.011 |
| pendulum_length_sweep | \(T \propto \sqrt{L}\) | \(T=2\pi\sqrt{L/g}\) | g ≈ 9.6–10.1 | 0.014 |
| ai_fake_freefall_veritas | uniform g | VERITAS: not_physical @ frame 41 | 6.1 m/s² implied | — |

Regenerate: `python3 -m evals --suite desk-mechanics --mode fixture` → `evals/results/`. Details: [`docs/EVALS.md`](docs/EVALS.md).

**Meta spend envelope (estimate):** `python3 scripts/cost_report.py` — sample sessions in `data/fixtures/cost_report_sample.json`; budget **~$150** credits per [`docs/HACKATHON_BRIEF.md`](docs/HACKATHON_BRIEF.md).

---

## Live Meta mode

1. Copy `.env.example` → `.env` and set `MODEL_API_KEY`
2. Set `FIXTURE_MODE=false` (or use Ops **live** on the lab UI)
3. Optional Meta probe: `./scripts/smoke_health.sh http://127.0.0.1:8000 meta`
4. Opt-in live smoke: `python scripts/smoke_meta_api.py`

**Spark Contributor:** `META_USE_CONTRIBUTOR=true` routes Observer Spark only — see [`docs/CONTRIBUTOR_ROUTING.md`](docs/CONTRIBUTOR_ROUTING.md).

---

## What it does (scientific loop)

1. **Observe** — Muse Spark scene brief + SAM prompts  
2. **Measure** — SAM 3.1 / calibrated trajectories → metres  
3. **Hypothesise** — rival laws; **held-out scoring** (maths decides)  
4. **Imagine** — Muse Image or geometric ghost; SAM audit error  
5. **Experiment** — Wonder PI: highest-information next test  
6. **Notebook** — accepted law + params + error bars  

Evidence table for the **25% Meta tooling** rubric: [`docs/META_EVIDENCE.md`](docs/META_EVIDENCE.md).

---

## Meta models (load-bearing)

| Model | Job | Code |
| --- | --- | --- |
| Muse Spark 1.3 | Observer | `services/api/hypatia/observer.py` |
| Muse Wonder 1.0 | PI plans + experiment | `services/api/hypatia/pi.py` |
| Muse Image 1.0 | Ghost frames | `services/api/hypatia/pipeline.py` |
| SAM 3.1 | Measure + audit | `services/api/hypatia/measurer.py` |
| Muse Glimmer (partners) | Hypothesis swarm | `services/api/hypatia/glimmer.py` |
| Muse Voice Transcribe | Hands-free lab | `services/api/hypatia/voice.py` |
| Muse Code | Build velocity (B-roll) | process / demo |

---

## Deploy (Meta partners first)

```bash
modal secret create hypatia-secrets MODEL_API_KEY=...
modal volume create hypatia-weights
# Finals only (Nov 4–9): MODAL_FINALS_WARM=1 modal deploy services/api/modal_app.py
modal deploy services/api/modal_app.py
```

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/MODAL_INTEGRATION.md`](docs/MODAL_INTEGRATION.md), [`docs/FINALS_WARM.md`](docs/FINALS_WARM.md). CI deploy: [`docs/GITHUB_ACTIONS_SECRETS.md`](docs/GITHUB_ACTIONS_SECRETS.md).

---

## Docs map

Start at [`docs/INDEX.md`](docs/INDEX.md). Judges: **HACKATHON_ALIGNMENT** → **META_EVIDENCE** → **SUBMISSION_PACK** → **DEMO_SCRIPT**.

---

## Built during the hackathon

Event window **Oct 26 – Nov 4, 2026 (ET)**. This public repo is the submission surface; commit history marks new work. See [`docs/HACKATHON_BRIEF.md`](docs/HACKATHON_BRIEF.md) for rubric weights (Impact 30%, Meta tooling 25%, Demo 25%, Depth 20%).

---

## License

MIT (intended). Third-party videos: [`data/videos/SOURCES.md`](data/videos/SOURCES.md).
