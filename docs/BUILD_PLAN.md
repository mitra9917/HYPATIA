# Build Plan — Phases, Milestones, Issues

Compressed schedule for the **remaining hackathon window** (Sun Nov 1 → Wed Nov 4, 2026 ET deadline).  
Full 10-day ideal plan is preserved as Appendix A for narrative / README.

## Operating rules

1. Docs first (this PR) → then issues/milestones → then code vertical slices.
2. Every milestone ends with a **demoable** artifact (screenshot/GIF/clip).
3. Prefer E2E thin slice over perfect modules.
4. Feature freeze: **Tue Nov 4, 8:00 PM IST** (afternoon ET Nov 4) for video day — adjust if shooting earlier.
5. Commit often on `cursor/*-db99` branches; keep `main` green.

---

## Phase 0 — Planning spine (NOW)

**Outcome:** architecture + win plan agreed; repo structure stubbed; no product code yet beyond placeholders.

| ID | Issue | Deliverable |
| --- | --- | --- |
| P0.1 | Research brief | `docs/HACKATHON_BRIEF.md` |
| P0.2 | Product spec | `docs/PRODUCT.md` |
| P0.3 | Architecture | `docs/ARCHITECTURE.md` |
| P0.4 | Meta tooling map | `docs/META_TOOLING.md` |
| P0.5 | Win strategy | `docs/WIN_STRATEGY.md` |
| P0.6 | Deployment plan | `docs/DEPLOYMENT.md` |
| P0.7 | Demo script | `demo/DEMO_SCRIPT.md` |
| P0.8 | Evals + risks | `docs/EVALS.md`, `docs/RISKS.md` |
| P0.9 | Repo skeleton map | `docs/REPO_STRUCTURE.md` |
| P0.10 | Agent conventions | `AGENTS.md` |

**Exit:** Mitrazzz reviews docs; we open Phase 1 issues and start coding.

---

## Phase 1 — Skeleton + perception vertical slice (Nov 1)

**Outcome:** upload/webcam clip → Spark SceneBrief → SAM masks → trajectory plot in UI.

| ID | Issue | Owner seat | Depends |
| --- | --- | --- | --- |
| P1.1 | Monorepo scaffold (api + web + compose) | Product | P0 |
| P1.2 | Meta client wrapper (Responses + Files) | Agent | P1.1 |
| P1.3 | Observer agent (Spark video → SceneBrief JSON) | Agent | P1.2 |
| P1.4 | SAM video measurer + parser | Vision | P1.2 |
| P1.5 | Calibration (A4 / coin) + SI trajectories | Vision | P1.4 |
| P1.6 | Session API + SSE progress | Agent | P1.1 |
| P1.7 | UI: upload, mask overlay, chart | Product | P1.6 |
| P1.8 | Record / gather 8–12 test videos + SOURCES.md | Science | — |
| P1.9 | Fixture recorder for offline replay | Agent | P1.3–P1.5 |

**Exit demo:** 30s GIF of pendulum masks + angle time series.

---

## Phase 2 — Hypothesis loop (Nov 2)

**Outcome:** rival theories → held-out scoring → first accepted law end-to-end.

| ID | Issue | Owner seat |
| --- | --- | --- |
| P2.1 | Equation DSL + PySR / SciPy fitter | Science |
| P2.2 | Glimmer swarm adapter (+ CPU stub) | Agent |
| P2.3 | Wonder PI orchestration (plan → measure → hypothesize) | Agent |
| P2.4 | Held-out gate + bootstrap CIs | Science |
| P2.5 | UI: hypothesis cards + scores | Product |
| P2.6 | Lab notebook markdown export | Product |
| P2.7 | Eval harness v0 on ≥5 clips | Science |

**Exit demo:** card shows \(T=2\pi\sqrt{L/g}\), \(g\approx9.7\pm0.4\).

---

## Phase 3 — Imagination, experiment, voice (Nov 3)

**Outcome:** ghost overlay + next-experiment prompt + voice turn.

| ID | Issue | Owner seat |
| --- | --- | --- |
| P3.1 | Predictor (kinematic / ODE forward) | Science |
| P3.2 | Muse Image ghost pipeline + mask hints | Vision |
| P3.3 | SAM imagination audit score | Vision |
| P3.4 | Geometric ghost fallback renderer | Vision |
| P3.5 | Experiment Designer (info gain) | Agent |
| P3.6 | Human-in-the-loop experiment UI | Product |
| P3.7 | Voice Transcribe → PI reply loop | Product/Agent |
| P3.8 | Hybrid/fixture mode switch | Agent |

**Exit demo:** ghost locks for 8+ seconds; UI asks to double string length.

---

## Phase 4 — Self-improvement + VERITAS + deploy (Nov 4)

**Outcome:** library memory, second domain, public deploy, evals table, video.

| ID | Issue | Owner seat |
| --- | --- | --- |
| P4.1 | Toolsmith sandbox (Modal or Docker) | Agent |
| P4.2 | Law + tool library persistence | Agent |
| P4.3 | Cell time-lapse path (reuse engine) | Vision/Science |
| P4.4 | VERITAS module on AI fall clip | Science |
| P4.5 | Computer-use PhET path (stretch) | Agent |
| P4.6 | Modal + Vercel deploy + health pings / warm containers | Product |
| P4.7 | Evals table in README | Science |
| P4.8 | Shoot + edit 3:00 demo video | Product |
| P4.9 | Submission package (form fields, links) | All |
| P4.10 | Public social clip + repo polish | Product |

**Exit:** submitted; uptime on; video unlisted/public as required.

---

## Milestone map (GitHub)

Suggested GitHub Milestones:

1. `M0 — Docs & skeleton`
2. `M1 — Perception E2E`
3. `M2 — First law`
4. `M3 — Ghost & experiment`
5. `M4 — Deploy, evals, submit`

Labels: `phase/0`…`phase/4`, `seat/agent`, `seat/vision`, `seat/science`, `seat/product`, `meta/spark`, `meta/wonder`, `meta/sam`, `meta/image`, `meta/glimmer`, `meta/voice`, `blocker`, `demo-critical`.

---

## Definition of Done (every issue)

- [ ] Code merged or clearly on PR
- [ ] Unit or fixture test where meaningful
- [ ] Cost-sensitive Meta calls behind client with logging
- [ ] README / module docstring updated if user-facing
- [ ] Demo note: how to show this in ≤20 seconds

---

## Appendix A — Ideal 10-day plan (from ideation PDF)

| Day (IST) | Goal |
| --- | --- |
| Mon 26 Oct | API access check; record test videos; SAM clone |
| Tue 27 | Observer + Measurer; trajectories |
| Wed 28 | Wonder PI + theorists + PySR; first law |
| Thu 29 | Predictor + Muse Image + SAM audit; ghost UI |
| Fri 30 | Experiment Designer + HITL + voice |
| Sat 31 | Toolsmith + library; cell domain |
| Sun 1 Nov | Glimmer swarm; VERITAS; computer-use PhET |
| Mon 2 | Evals + feature freeze |
| Tue 3 | Demo video day |
| Wed 4 | README, cleanup, viral post, submit (hard deadline Thu 5 Nov 7:30 AM IST) |

We are entering at **Sun 1 Nov** relative to that plan → execute Phases 1–4 as the compressed critical path; cut stretch before cutting ghost or held-out gates.
