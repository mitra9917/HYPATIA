# HYPATIA Documentation Index

Read in this order before opening issues or coding:

| # | Doc | Purpose |
| --- | --- | --- |
| 1 | [HACKATHON_BRIEF.md](./HACKATHON_BRIEF.md) | Event rules, dates, rubric, Meta stack, pass/fail gates |
| 2 | [PRODUCT.md](./PRODUCT.md) | What HYPATIA does, users, capabilities, novelty |
| 3 | [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, agents, APIs, data model |
| 4 | [META_TOOLING.md](./META_TOOLING.md) | How every Meta model is used (25% category) |
| 4b | [META_COVERAGE_STATUS.md](./META_COVERAGE_STATUS.md) | Playbook #1 live matrix — scaffold vs verified |
| 5 | [WIN_STRATEGY.md](./WIN_STRATEGY.md) | Campaign to clear finals and win Indie track |
| 6 | [BUILD_PLAN.md](./BUILD_PLAN.md) | Phases, milestones, issue IDs, DoD |
| 7 | [DEPLOYMENT.md](./DEPLOYMENT.md) | Modal-first deploy (Vercel + GPU + R2/S3); AWS as later path |
| 8 | [EVALS.md](./EVALS.md) | Metrics and harness |
| 9 | [RISKS.md](./RISKS.md) | Failures, kill order, live incident runbook |
| 10 | [REPO_STRUCTURE.md](./REPO_STRUCTURE.md) | Monorepo layout |
| 11 | [NEXT_ISSUES.md](./NEXT_ISSUES.md) | First GitHub issues to file after docs merge |

Also:

- [../demo/DEMO_SCRIPT.md](../demo/DEMO_SCRIPT.md) — 3-minute video script
- [../AGENTS.md](../AGENTS.md) — coding conventions for humans and agents
- [../README.md](../README.md) — public face of the repo

## Implementation status

Scaffold is in-repo:

- `services/api` — FastAPI science loop (fixture E2E green; Meta live hooks)
- `apps/web` — Next.js lab UI with ghost overlay
- `services/api/modal_app.py` — Meta-partner Modal deploy
- `infra/aws/` — AWS fallback notes (priority #2)
- `docker-compose.yml` — local full stack

## Next actions

1. Set `MODEL_API_KEY`, run `python scripts/smoke_meta_api.py`  
2. `modal deploy services/api/modal_app.py`  
3. Wire real SAM video file tracking on uploads  
4. Glimmer on Modal GPU / Baseten / Fireworks  
5. Record demo videos + shoot 3:00 clip  
6. AWS S3 bucket for media if not using only Modal Volumes  
