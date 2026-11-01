# HYPATIA — System Architecture

## 1. Design principles

1. **LLM proposes, maths decides.** A law ships only if it beats rivals on held-out future frames (prediction error, R²) with bootstrap error bars.
2. **Every Meta tool has a load-bearing job.** If removing it does not break a visible demo beat, we are using it wrong.
3. **Perceive → reason → act → improve.** Superintelligence test on every feature.
4. **Cost-aware routing.** Wonder = PI brain; Spark = fast multimodal loops; Glimmer = bulk swarm; cache SAM.
5. **Demo-first reliability.** Offline clips + cached API fixtures always available for live judging.

## 2. High-level diagram

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Next.js)                                 │
│  Webcam / Upload │ Mask Overlay │ Trajectory Charts │ Hypothesis Cards   │
│  Ghost Overlay   │ Experiment Prompt │ Voice Mic │ Lab Notebook          │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ REST + WebSocket / SSE
┌───────────────────────────────▼──────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                               │
│  /sessions  /observe  /measure  /hypothesize  /predict  /experiment      │
│  /imagine   /audit    /voice    /notebook     /library                   │
└───┬─────────┬─────────┬─────────┬─────────┬─────────┬────────────────────┘
    │         │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼         ▼
 Observer  Measurer   PI Agent  Predictor  Imagination  Toolsmith
 Spark     SAM 3.1    Wonder    Law→sim    Muse Image   Wonder+Sandbox
 video     tracking   +swarm    SciPy      + SAM audit  (Modal/Docker)
                      Glimmer
                      PySR
    │         │         │         │         │         │
    └─────────┴─────────┴────┬────┴─────────┴─────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Persistence (Postgres)       │
              │ sessions, trajectories, laws │
              │ tools, notebooks, evals      │
              └──────────────────────────────┘
              ┌──────────────────────────────┐
              │ Object / video store         │
              │ R2 or S3 + Modal Volumes     │
              │ (weights / fixture cache)    │
              └──────────────────────────────┘
```

## 3. Agent roles (runtime)

| Agent | Model | Responsibility | Tools |
| --- | --- | --- | --- |
| **Principal Investigator (PI)** | `muse-wonder-1.0` | Campaign plan, spawn sub-agents, decide when to stop, ask human for experiment, optional computer use | `spawn_theorist`, `run_toolsmith`, `request_experiment`, `computer`, library CRUD |
| **Observer** | `muse-spark-1.3` | Watch clip / webcam burst; name objects; propose variables; write SAM prompts; narrate | video/image input, structured JSON schema |
| **Measurer** | `sam-3.1` + OpenCV | Masks, identity tracking, centroid/angle/length → SI units via calibration | Files API, `meta_sam_parser` |
| **Theorist swarm** | Muse Glimmer (local) + Spark | Propose rival functional forms; pre-screen | equation DSL |
| **Symbolic fitter** | PySR / SciPy | Fit constants; score held-out prediction | NumPy trajectories |
| **Predictor** | deterministic + Spark explain | Simulate future states from accepted candidates | ODE / kinematic solvers |
| **Imagination** | `muse-image-1.0` | Edit current frame → predicted next frame (ghost) | `/v1/images/edits` or Responses multi-turn |
| **Auditor** | `sam-3.1` | Measure imagined frame vs real frame; score physics fidelity | image segmentation |
| **Experiment Designer** | Wonder (via PI) | Expected information gain over rival posterior | scoring utilities |
| **Toolsmith** | Wonder + sandbox | Write measurement/sim code; unit-test on recorded frames; promote to library | Modal sandbox / Docker |
| **Voice** | `muse-voice-transcribe-1.0` | Hands-free experiment dialogue | realtime ASR WS or file ASR |
| **VERITAS** (module) | Spark + Measurer + known laws | Detect physics breaks in AI video | same measurement stack |

## 4. End-to-end session flow

```text
1. CREATE SESSION
   client → POST /sessions {source: webcam|upload|url}
   store video file_id (Meta Files API and/or our blob)

2. OBSERVE
   Spark(video) → SceneBrief {
     objects: [{name, why_interesting}],
     candidate_variables: [...],
     sam_prompts: ["pendulum bob", "string", "A4 sheet"],
     suggested_domain: "mechanics.pendulum"
   }

3. MEASURE
   for prompt in sam_prompts:
     SAM video track → masks[t], boxes[t], object_id
   calibrate(scale_object) → metres_per_pixel
   trajectories = extract_time_series(masks, fps, scale)
   persist CSV + plot payloads

4. HYPOTHESIZE (parallel)
   Glimmer swarm → N candidate forms
   PySR → fit on train window [0, t_split)
   score each on held-out [t_split, T]
   PI ranks rivals; keep top-k

5. IMAGINE + AUDIT (for top rivals)
   Predictor → state(t+Δ)
   Muse Image edits frame_t → framê_{t+Δ}
   SAM measures framê vs real frame_{t+Δ}
   UI shows ghost + error meter

6. EXPERIMENT
   Experiment Designer → NextTest {instruction, expected_outcomes_per_theory}
   Human does it OR computer-use drives simulator
   Re-measure → Bayesian / likelihood update → eliminate losers

7. ACCEPT LAW
   Only if held-out metrics + rival comparison pass gates
   Write LabNotebook {law, constants±err, video, code, tools_used}
   Upsert LawLibrary + ToolLibrary
```

## 5. Data model (minimal)

```text
Session
  id, created_at, source_type, status, meta_file_ids[], domain_hint

Observation
  session_id, scene_brief_json, model, tokens_used

Track
  session_id, object_name, sam_prompt, mask_uri, trajectory_json

Hypothesis
  session_id, form_latex, params_json, train_score, heldout_score, status

Experiment
  session_id, instruction, expected_json, result_json, info_gain

ImaginationAudit
  hypothesis_id, frame_t, predicted_uri, real_uri, sam_error, score

Tool
  name, source, tests_json, adopted_at, session_origin

Law
  form_latex, params_json, domain_tags, evidence_session_ids[], confidence

Notebook
  session_id, markdown, export_uri
```

Hackathon persistence: **Postgres** (Neon or Supabase). Media: **R2/S3**. Open-weight caches: **Modal Volumes**. Local `./data` only for docker-compose dev.

## 6. Repository layout (target)

```text
hypatia/
├── apps/
│   └── web/                 # Next.js UI (overlays, cards, ghost, voice)
├── services/
│   └── api/                 # FastAPI gateway + orchestration
├── packages/
│   ├── agents/              # PI, Observer, Experiment Designer prompts + loops
│   ├── vision/              # SAM client, calibration, trajectories
│   ├── science/             # PySR, scoring, physics priors, VERITAS
│   ├── imagination/         # Muse Image ghost pipeline
│   ├── toolsmith/           # sandbox runner + library
│   └── meta/                # shared Model API client wrappers
├── data/
│   ├── fixtures/            # cached API responses for offline demo
│   └── videos/              # test clips ( Pendulum, cells, fake fall )
├── evals/                   # law recovery, active vs passive, audit scores
├── demo/                    # script, shot list, captions
├── docs/                    # this documentation set
├── scripts/                 # smoke tests, cost report, seed library
├── modal_app.py             # Modal deploy entry (API + GPU + sandboxes)
├── docker-compose.yml       # local dev
└── README.md
```

Monorepo is fine for a 10-day hack; keep Python science stack in `services/api` + `packages/*` and TypeScript only in `apps/web` if team prefers fewer moving parts. **Allowed simplification for remaining days:** single FastAPI service serving a Next.js frontend, with packages as Python modules under `services/api/hypatia/`.

## 7. API surface (v1)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/sessions` | Create session; accept upload or start webcam proxy |
| GET | `/api/sessions/{id}` | Status + stage |
| POST | `/api/sessions/{id}/observe` | Run Observer |
| POST | `/api/sessions/{id}/measure` | Run SAM + trajectories |
| POST | `/api/sessions/{id}/hypothesize` | Swarm + fit + rank |
| POST | `/api/sessions/{id}/imagine` | Ghost for hypothesis |
| POST | `/api/sessions/{id}/experiment/propose` | Next test |
| POST | `/api/sessions/{id}/experiment/result` | Human/simulator outcome |
| POST | `/api/sessions/{id}/accept` | Commit law + notebook |
| GET | `/api/sessions/{id}/events` | SSE progress for UI |
| POST | `/api/voice/turn` | Transcribe + PI reply |
| GET | `/api/library/laws` | Learned laws |
| GET | `/api/health` | Liveness for Modal / Vercel proxy |

## 8. Meta Model API integration rules

- Base URL: `https://api.meta.ai/v1`
- Default protocol: **Responses API** for agents; Chat Completions only for trivial helpers
- Model IDs hardcoded in one `ModelRouter` (easy swap Spark ↔ Wonder)
- Prompt caching for repeated PI system prompts
- Structured outputs (JSON schema) for SceneBrief, HypothesisBatch, NextTest
- Files API for reusable video `file_id`s
- Computer use only on Wonder (or Spark for cheaper CUA loops) against a controlled PhET browser in a sandbox VM
- SAM: stream video when possible; decode with `meta_sam_parser`
- Never log raw API keys; never commit `.env`

## 9. Calibration & science gates

**Calibration**

- Scale: A4 sheet (210×297 mm) or ₹10 coin diameter in frame
- Time: container FPS / timestamps
- Optional: OpenCV checkerboard undistort

**Acceptance gates for a law**

1. Held-out RMSE / R² better than all rivals by margin δ
2. Physical priors not wildly violated (unless VERITAS mode expects violation)
3. Parameter CI from bootstrap does not include nonsense (e.g. negative length)
4. Imagination audit mean error below threshold **or** honest fallback to geometric ghost renderer

## 10. Failure modes & graceful degradation

| Failure | UX / engineering fallback |
| --- | --- |
| Muse Image placement imprecise | Mask-hinted edit; else render geometric ghost; still SAM-audit whatever is drawn |
| SAM rate / latency | Cache tracks; open SAM weights on Modal; offline fixture playback |
| Wonder cost spike | PI plan once → Spark executes steps |
| Hallucinated equation | Held-out gate blocks acceptance; show rivals fighting |
| Network blip on live demo | Switch to fixture mode with banner "replay mode" |

## 11. Security & ethics

- Public demo: no uploading of sensitive lab IP without consent banner
- VERITAS: educational / integrity tool — not a courtroom claim without human review
- Sandbox Toolsmith: no host network by default; resource limits; allowlist imports
- Respect Meta Contributor mode policy: use Contributor for non-sensitive test loops only; Standard for anything we would mind training on

## 12. Why this architecture scores

| Rubric | Architecture lever |
| --- | --- |
| Impact 30% | Real users (schools, labs) + product path + reproducible notebook |
| Meta tooling 25% | Six Meta surfaces, four "unexpected capabilities" (see META_TOOLING.md) |
| Demo 25% | Ghost overlay + experiment ask + cross-domain drop-in |
| Technical depth 20% | Held-out validation, sandboxed self-tooling, eval suite, cost router |
