# Meta Global AI Developer Hackathon — HYPATIA alignment

> **Event:** [Meta Global AI Developer Hackathon](https://cerebralvalley.ai/e/meta-ai-developer-hackathon) (Cerebral Valley)  
> **Track:** Indie developer · **Theme:** Push the Frontier  
> **Repo:** public · **Built in window:** Oct 26 – Nov 4, 2026 (ET)

This document is written for **judges and automated review**: it maps HYPATIA to official gates, rubric weights, and Meta tooling requirements.

## Stage One — pass / fail

| Gate | HYPATIA evidence |
| --- | --- |
| Fits theme (Build for Your World **or** Push the Frontier) | Push the Frontier: camera + scientific method on never-seen motion; cross-domain cells; VERITAS on synthetic physics |
| Uses **Meta Model API** and/or **Meta open weights** | Spark Observer, Wonder PI, Muse Image, SAM 3.1, Voice Transcribe — see [`META_TOOLING.md`](./META_TOOLING.md) §5 |
| Open source | This repository (MIT) |
| New work in hackathon window | [`README.md`](../README.md) § Built during the hackathon + git history |

## Stage Two — rubric (what we optimize)

| Category | Weight | HYPATIA proof in repo |
| --- | ---: | --- |
| **Impact** | 30% | Schools-without-labs narrative [`PRODUCT.md`](./PRODUCT.md); live desk pendulum → law card; [`demo/DEMO_SCRIPT.md`](../demo/DEMO_SCRIPT.md) |
| **Meta AI tooling** | 25% | SAM as ruler; Wonder PI + Toolsmith; Image ghost audited by SAM; Glimmer swarm — [`META_EVIDENCE.md`](./META_EVIDENCE.md) |
| **Demo** | 25% | Fixture-safe E2E + ops flip [`DEMO_RELIABILITY.md`](./DEMO_RELIABILITY.md); `./scripts/smoke_playbook_52_57.sh` |
| **Technical depth** | 20% | Held-out scoring [`scoring_gate.py`](../services/api/hypatia/scoring_gate.py); evals [`EVALS.md`](./EVALS.md); CI fixture tests |

## Meta Model API (required path)

| Model ID | HYPATIA role | Code entry |
| --- | --- | --- |
| `muse-spark-1.3` (+ contributor optional) | Observer scene brief | `services/api/hypatia/observer.py` |
| `muse-wonder-1.0` | PI phase plans | `services/api/hypatia/pi.py` |
| `muse-image-1.0` | Ghost imagination | `services/api/hypatia/pipeline.py` |
| `sam-3.1` | Measure + audit | `services/api/hypatia/measurer.py` |
| `muse-voice-transcribe-1.0` | Voice loop | `services/api/hypatia/voice.py` |
| Muse Glimmer (open weights) | Hypothesis swarm | `services/api/hypatia/glimmer.py` + Modal GPU |

**Partner inference (Meta-listed):** Modal (primary deploy), Baseten/Fireworks (Glimmer failover) — [`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Submission checklist (Indie track)

- [ ] Public GitHub repo URL (this repo)
- [ ] **Demo video** (~3 min) — script: [`demo/DEMO_SCRIPT.md`](../demo/DEMO_SCRIPT.md)
- [ ] **Live URL** — Modal ASGI + Vercel web ([`PRODUCTION_DEPLOY_CHECKLIST.md`](./PRODUCTION_DEPLOY_CHECKLIST.md))
- [ ] README: theme, models, how to run, what was built during hackathon
- [ ] No secrets in git — `.env.example` only

## Validation commands (local / CI)

```bash
bash scripts/verify_playbook_58_62.sh      # docs + unit/integration
./scripts/run_api_local.sh                 # terminal 1
./scripts/smoke_playbook_52_57.sh          # live API smoke (52–57)
python scripts/cost_report.py              # credit envelope vs fixture sample
python -m evals.run --suite desk-mechanics --mode fixture
```

## Finals warm path (Nov 4–9)

See [`FINALS_WARM.md`](./FINALS_WARM.md) — `min_containers=1` on Modal when `MODAL_FINALS_WARM=1`, scheduled `/api/health` ping via [`.github/workflows/warm-health.yml`](../.github/workflows/warm-health.yml).
