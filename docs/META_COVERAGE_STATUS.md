# Meta tooling coverage status (Playbook #1)

Living audit for **[GitHub #44](https://github.com/mitra9917/HYPATIA/issues/44)**.  
Update this file when a row moves stage; mirror checkboxes on #44.

**Legend**

| Status | Meaning |
| --- | --- |
| **NOT** | No code path yet |
| **SCAFFOLD** | Wired with fixture / stub / fallback |
| **LIVE** | Live Meta call on happy path (needs `MODEL_API_KEY`) |
| **VERIFIED** | Live + logged in demo/README with file path |
| **HUMAN** | You configure keys/accounts (integration issue) |
| **PROCESS** | Muse Code B-roll / narrative (not runtime) |

**Last audit:** 2026-11-02 (Playbook #12 — docs spine verified)

---

## M0 integration spine (Playbook #12)

| Issue | Status | Notes |
| --- | --- | --- |
| #2 Meta API | Done | smoke `meta: True` |
| #3 Modal | Done | `modal setup` |
| #4 Glimmer | Done | `GLIMMER_PROVIDER=stub`; Modal GPU at deploy (#47) |
| #5 Postgres | Done | Supabase |
| #48 S3 | Done | bucket + smoke |
| #6 Vercel | Done | `apps/web` |
| #7 Muse Code | Done | B-roll + Muse CLI |
| #8 Spark Open | Skipped | API `muse-spark-1.3` primary — reopen if rate limits |
| #45 Baseten | Skipped / key | optional Glimmer failover |
| #46 Fireworks | Skipped | optional |
| #47 Modal secrets | **Open** | at `modal deploy` (Playbook ~#50) |
| #49 GitHub Actions | **Open** | before CI deploy secrets |

---

## Required Meta Model API

| Tool | Model ID | Status | Code / module | Playbook / issue | Demo beat |
| --- | --- | --- | --- | --- | --- |
| Muse Spark (Observer) | `muse-spark-1.3` | SCAFFOLD | `pipeline._observe`, `meta_client.respond_text` | #11–13, #58 | Open-vocab scene → SAM prompts |
| Spark Contributor | `…-contributor` | SCAFFOLD | `config.observer_model` | #54, #2 | Cost routing for observer loops |
| Muse Wonder (PI) | `muse-wonder-1.0` | SCAFFOLD | `pipeline._hypothesize`, `_experiment` | #21, #30 | PI narration + experiment phrasing |
| Muse Image | `muse-image-1.0` | SCAFFOLD | `meta_client.generate_image`, `pipeline._imagine` | #27 | Ghost / predicted frame |
| SAM 3.1 | `sam-3.1` | **MEASURER (P1.4)** | `hypatia/measurer.py`, `sam_decode.py` (stub until #51) | #13, #28, #51 | Masks → SI trajectories + audit |
| Muse Voice | `muse-voice-transcribe-1.0` | NOT | (no `/api/voice/turn` yet) | #32, #59 | Hands-free experiment Q&A |

## Open weights

| Tool | Status | Code / module | Playbook / issue |
| --- | --- | --- | --- |
| Muse Glimmer | SCAFFOLD (stub + Modal fn) | `hypatia/glimmer.py`, `modal_app.glimmer_swarm` | #4, #20, #45–46 |
| Muse Spark Open | SKIPPED (API `muse-spark-1.3` primary) | — | #8 |

## API surfaces

| Surface | Status | Code / module | Playbook / issue |
| --- | --- | --- | --- |
| Responses API | SCAFFOLD | `meta_client.respond_text` | #11 |
| JSON schema outputs | SCAFFOLD | SceneBrief in `pipeline._observe` | #58 |
| Files API (video `file_id`) | NOT | — | #50 |
| Images API | SCAFFOLD | `meta_client.generate_image` | #27 |
| meta_sam_parser (Python) | **IN** | `requirements.txt`, `sam_parser_bridge.py` | #51 |
| @meta-sam/parser (web) | NOT | — | #51 |
| Voice realtime WS | NOT | — | #59 |
| Computer use (Wonder) | NOT | — | #38, #68 |

## Dev & partners

| Item | Status | Playbook / issue |
| --- | --- | --- |
| Muse Code (process proof) | HUMAN | #7 |
| Meta Model API key | HUMAN | **#2** ← next |
| Modal | HUMAN | #3, #47 |
| Vercel web | HUMAN | #6 |
| Postgres | HUMAN | #5, #55 |
| S3 media | HUMAN | #48 |
| Baseten / Fireworks | HUMAN (optional) | #45–46 |
| GitHub Actions secrets | HUMAN | #49 |

---

## Stage One / rubric gates

- [ ] **Pass/fail:** At least one **VERIFIED** live Meta Model API call + one **VERIFIED** open-weight (Glimmer) path before submission.
- [ ] **25% tooling:** Each row above either **VERIFIED** or explicitly demoed via fixture with honest README note.
- [ ] **Evidence table:** Copy completed rows into README (P4.7 / #40) with demo timestamps.

---

## Next playbook steps (after M0)

1. **Playbook #13** — Code: **P1.1** monorepo hardening ([#10](https://github.com/mitra9917/HYPATIA/issues/10)).
2. **Playbook #47 / #50** — Modal secrets + deploy when API goes cloud.
3. **Playbook #49** — GitHub Actions secrets before CI deploy path.
