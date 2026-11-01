# HYPATIA

**The camera that does science.**

Point any camera at anything that moves. HYPATIA finds the law behind it, proves the law by predicting the future, then tells you which experiment to run next. It gets faster with every video.

> We gave Meta's models a camera and the scientific method. It rediscovered Galileo on my desk in 90 seconds.

Built for the **Meta Global AI Developer Hackathon** (Cerebral Valley) — **Indie track** · theme **Push the Frontier**.

| | |
| --- | --- |
| Status | Planning docs complete → Phase 1 coding next |
| Submission deadline | **Nov 4, 2026, 9:00 PM ET** (Nov 5, 7:30 AM IST) |
| Live app | _TBD after deploy_ |
| Demo video | _TBD_ |

---

## Why this wins the gate + rubric

| Rubric | How HYPATIA answers |
| --- | --- |
| **Pass/fail** | Uses Meta Model API + open weights; Push the Frontier (accelerate experiments, understand physical systems, models meet the real world) |
| **Impact 30%** | ~1.25 lakh Indian secondary schools without labs; research video overload; reproducible notebooks; path to world-model training data |
| **Meta tooling 25%** | Spark, Wonder, Image, SAM 3.1, Glimmer, Voice, Muse Code — each load-bearing; four "unexpected capabilities" |
| **Demo 25%** | Live ghost prediction overlay; cross-domain drop-in; VERITAS physics watermark beat |
| **Depth 20%** | Held-out law gates, sandboxed self-tooling, eval suite, cost-aware model router |

---

## What it does

1. **Observe** — Muse Spark watches the video and decides what to measure  
2. **Measure** — SAM 3.1 tracks open-vocabulary objects; calibration turns pixels into metres  
3. **Hypothesise** — Muse Wonder runs a PI campaign; Glimmer proposes rival laws; PySR fits; maths decides  
4. **Imagine** — Muse Image draws the predicted future; SAM audits imagination vs reality  
5. **Experiment** — HYPATIA asks for the single best next test (or drives a simulator via computer use)  
6. **Learn** — surviving laws and tools go into a library; the next session is cheaper and faster  

Same engine on a desk pendulum, a microscopy time-lapse, or an AI-generated fake — **no new product code**.

---

## Meta models used

| Model | Role in HYPATIA |
| --- | --- |
| Muse Spark 1.3 | Multimodal Observer (video → scene brief + SAM prompts) |
| Muse Wonder | Principal Investigator, Experiment Designer, Toolsmith, computer use |
| Muse Image | Predicted-frame "ghost" + notebook diagrams |
| SAM 3.1 | Scientific measuring instrument + imagination auditor |
| Muse Glimmer (open weights) | Offline hypothesis swarm |
| Muse Voice Transcribe | Hands-free experiment dialogue |
| Muse Code | Build agent (process authenticity in demo) |

Details: [`docs/META_TOOLING.md`](docs/META_TOOLING.md)

---

## Documentation (start here)

Full index: [`docs/INDEX.md`](docs/INDEX.md)

| Doc | Contents |
| --- | --- |
| [Hackathon brief](docs/HACKATHON_BRIEF.md) | Rules, dates, prizes, rubric, API pricing |
| [Product](docs/PRODUCT.md) | Capabilities, users, novelty claim |
| [Architecture](docs/ARCHITECTURE.md) | Agents, APIs, data model, diagrams |
| [Win strategy](docs/WIN_STRATEGY.md) | How we clear finals |
| [Build plan](docs/BUILD_PLAN.md) | Phases P0–P4, milestones, issue IDs |
| [Deployment](docs/DEPLOYMENT.md) | Modal-first (Vercel + GPU Volumes + R2/S3); not Render free |
| [Demo script](demo/DEMO_SCRIPT.md) | 3-minute shot list |
| [Evals](docs/EVALS.md) / [Risks](docs/RISKS.md) | Proof + kill order |
| [AGENTS.md](AGENTS.md) | Conventions for contributors & coding agents |

---

## Built during the hackathon

**Event window:** Oct 26 – Nov 4, 2026 (ET).

This repository's planning spine and subsequent implementation commits are produced inside the event window for the Indie submission. The README will list the commit range and feature checklist before submit so judges can clearly identify new work (hackathon rule).

Prior ideation notes (local PDF) informed product choice only; product code starts after these docs.

---

## Repo status

```text
docs/     ✅ planning complete (this PR)
demo/     ✅ script draft
apps/     ⏳ Phase 1 scaffold next
services/ ⏳ Phase 1 scaffold next
evals/    ⏳ after first law loop
```

---

## Quick links

- Event: https://cerebralvalley.ai/e/meta-ai-developer-hackathon  
- Event details: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details  
- Meta Model API: https://dev.meta.ai/docs/overview  
- Meta hackathon page: https://dev.meta.ai/events/global-hackathon  

---

## License

To be set before public launch (prefer MIT or Apache-2.0 for hackathon openness). Do not commit third-party assets without rights — see `data/videos/SOURCES.md` (forthcoming).
