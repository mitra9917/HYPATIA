#!/usr/bin/env python3
"""Add gap-fill issues for end-to-end coverage (Meta tools, frontend, business logic)."""
from __future__ import annotations

import json
import subprocess
import sys

REPO = "mitra9917/HYPATIA"


def gh_json(*args: str):
    out = subprocess.check_output(["gh", *args], text=True)
    return json.loads(out) if out.strip() else None


def existing_titles() -> set[str]:
    titles: set[str] = set()
    page = 1
    while True:
        data = gh_json(
            "api",
            f"repos/{REPO}/issues?state=all&per_page=100&page={page}",
        )
        if not data:
            break
        for item in data:
            if "pull_request" not in item:
                titles.add(item["title"])
        if len(data) < 100:
            break
        page += 1
    return titles


def create_label(name: str, color: str, desc: str) -> None:
    subprocess.run(
        ["gh", "label", "create", name, "--color", color, "--description", desc, "--repo", REPO],
        capture_output=True,
    )


def create_issue(title: str, milestone: str, labels: list[str], body: str) -> None:
    subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--repo",
            REPO,
            "--title",
            title,
            "--milestone",
            milestone,
            "--label",
            ",".join(labels),
            "--body",
            body,
        ],
        check=True,
    )


NEW_LABELS = [
    ("frontend", "E99695", "Next.js UI, UX, client integrations"),
    ("business-logic", "1D76DB", "Science loop orchestration and gates"),
    ("infra/ci", "0E8A16", "GitHub Actions, deploy automation"),
    ("meta/files", "0075CA", "Meta Files API"),
    ("meta/responses", "0052CC", "Meta Responses API + JSON schema"),
    ("meta/computer", "5319E7", "Wonder computer use tool"),
    ("meta/contributor", "BFD4F2", "Spark Contributor mode policy"),
]

M0 = "M0 — Docs & integration spine"
M1 = "M1 — Perception E2E"
M2 = "M2 — First law"
M3 = "M3 — Ghost & experiment"
M4 = "M4 — Deploy, evals, submit"

ISSUES: list[tuple[str, str, list[str], str]] = [
    (
        "P0.12 — TRACKING: Meta models, APIs & open weights coverage matrix",
        M0,
        ["phase/0", "seat/product", "business-logic", "blocker"],
        """## Purpose
Single checklist so **nothing falls through** for the 25% Meta tooling rubric and Stage One pass/fail.

## Must ship evidence for each row (README + demo timestamp)

| Requirement | Model / surface | Primary issues | Module target |
| --- | --- | --- | --- |
| Observer / narration | `muse-spark-1.3` | #12, #11, #2 | `hypatia/agents/observer` or pipeline observe |
| Spark Contributor (cost) | `muse-spark-1.3-contributor` | #54, #2 | `ModelRouter` |
| PI / Toolsmith / experiment | `muse-wonder-1.0` | #21, #30, #34, #38 | `agents/pi`, toolsmith |
| Ghost / diagrams | `muse-image-1.0` | #27 | `imagination/` |
| Scientific ruler + audit | `sam-3.1` | #13, #28, #37 | `vision/sam` |
| Hypothesis swarm (open) | **Muse Glimmer** | #4, #20 | `science/swarm` |
| Voice | `muse-voice-transcribe-1.0` | #32, #59 | `/api/voice/turn` |
| Dev process | **Muse Code** | #7 | README + B-roll |
| Optional fallback | **Muse Spark Open** | #8 | hybrid router |
| Protocol | **Responses API** + **Files API** | #11, #50 | `meta_client.py` |
| Stretch | **Computer use** | #38 | PhET sandbox |
| Client decode | **meta_sam_parser** / `@meta-sam/parser` | #51 | API + optional web |

## Definition of done
- [ ] Every row has a merged PR or explicit "demo uses fixture X" note
- [ ] P4.7 README table copied from this matrix with file paths filled in
- [ ] Comment on this issue when each row turns green
""",
    ),
    (
        "[INTEGRATION] Baseten account + hackathon credits (Glimmer failover)",
        M0,
        ["integration-human", "meta/glimmer", "phase/0"],
        """## When
Before M2 demo if Modal GPU is slow/unavailable (`docs/DEPLOYMENT.md` §6).

## What YOU do
1. Sign up / redeem **Baseten** hackathon credits (event partner).
2. Deploy **Muse Glimmer** (or Meta open-weight endpoint from workshop) → copy inference URL + API key.
3. `.env`: `BASETEN_API_KEY=`, set `GLIMMER_PROVIDER=baseten` when P2.2 adapter supports it.

## DoD
- [ ] One successful curl from your machine OR comment "skipped — Modal only" with reason
""",
    ),
    (
        "[INTEGRATION] Fireworks account + hackathon credits (Glimmer failover)",
        M0,
        ["integration-human", "meta/glimmer", "phase/0"],
        """## When
Tertiary failover if Modal + Baseten both fail.

## What YOU do
1. Fireworks console → API key → `FIREWORKS_API_KEY=`
2. Deploy/host Glimmer per Meta workshop; `GLIMMER_PROVIDER=fireworks`

## DoD
- [ ] Key in `.env` only; comment provider choice on #4
""",
    ),
    (
        "[INTEGRATION] Modal Secrets + Volume (hypatia-weights) + S3 mount prep",
        M0,
        ["integration-human", "phase/0", "phase/4", "blocker"],
        """## When
Before **P4.6** production deploy (`docs/DEPLOYMENT.md` §5).

## What YOU do
```bash
modal volume create hypatia-weights
modal secret create hypatia-secrets \\
  MODEL_API_KEY=... \\
  DATABASE_URL=... \\
  AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... S3_BUCKET=... \\
  GLIMMER_PROVIDER=modal FIXTURE_MODE=false
```
- Never paste secrets in GitHub issues — comment "secrets created in Modal" only.

## DoD
- [ ] `modal secret list` shows `hypatia-secrets`
- [ ] Volume exists for weight/fixture cache
""",
    ),
    (
        "[INTEGRATION] AWS S3 media bucket (Modal-primary still uses S3)",
        M0,
        ["integration-human", "phase/0", "phase/4"],
        """## Why
`pipeline.py` already calls `upload_bytes_to_s3`; judges expect durable media (`DEPLOYMENT.md` §7).

## What YOU do
1. Create bucket `hypatia-media` (or your name) in `ap-south-1`.
2. IAM user with `s3:PutObject/GetObject` on prefix `uploads/`.
3. `.env`: `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`.

## DoD
- [ ] Local upload creates object `uploads/{session_id}/...`
""",
    ),
    (
        "[INTEGRATION] GitHub Actions secrets (CI deploy)",
        M0,
        ["integration-human", "infra/ci", "phase/0", "phase/4"],
        """## When
Before **P4.11** CI deploy workflow merges.

## Repo secrets to add (Settings → Secrets → Actions)
- `MODEL_API_KEY` (optional: smoke on main only)
- `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` (if using Vercel CLI deploy)

## DoD
- [ ] Comment "GH secrets configured" — no values in comment
""",
    ),
    (
        "P1.10 — Meta Files API: upload-once video file_id reuse",
        M1,
        ["phase/1", "seat/agent", "meta/files", "meta/responses", "demo-critical"],
        """## Business logic
ARCHITECTURE §4 step 1: store Meta `file_id` on Session; **Observer + SAM must reuse** — no double upload (cost + latency).

## Tasks
- [ ] `POST /v1/files` wrapper in `meta_client.py`
- [ ] Persist `meta_file_ids[]` on session row
- [ ] Observer + SAM calls use same `file_id`
- [ ] Fallback: local path only in fixture mode

## DoD
- [ ] Log shows one upload per session in live mode
- [ ] Depends: #11, INTEGRATION Meta key #2
""",
    ),
    (
        "P1.11 — SAM decode: meta_sam_parser (Python) + optional @meta-sam/parser (web)",
        M1,
        ["phase/1", "seat/vision", "meta/sam", "frontend", "demo-critical"],
        """## Hackathon stack
- Backend: `meta_sam_parser` (Python) per `AGENTS.md`
- Frontend (optional): `@meta-sam/parser` if streaming masks to browser without heavy server PNGs

## Tasks
- [ ] Harden decode in measurer; stable object IDs across frames
- [ ] Document when client-side decode is used vs server-side overlay JSON
- [ ] Unit test decode on fixture SAM payload

## DoD
- [ ] Masks render in UI (#16) from decoded tracks
""",
    ),
    (
        "P1.12 — Frontend lab shell: stage stepper, SSE, errors, mode banner",
        M1,
        ["phase/1", "seat/product", "frontend", "demo-critical", "business-logic"],
        """## Business logic
User must **see** the closed loop stages (`docs/ARCHITECTURE.md` §4):
`created → observe → measure → hypothesize → imagine → experiment → accept`

## Scope (`apps/web`)
- [ ] Stepper / timeline bound to session.status + SSE events (#15)
- [ ] Subscribe to `GET /api/sessions/{id}/events` (not only blocking `runSession`)
- [ ] Surface `session.error`, retry guidance per `docs/RISKS.md`
- [ ] Fixture/hybrid/live banner (ties #18, #33)
- [ ] `apps/web/lib/api.ts` typed client for all v1 routes in ARCHITECTURE §7

## DoD
- [ ] Upload flow shows per-stage progress without silent 60s wait
- [ ] Works on Vercel preview with `API_ORIGIN` (#6)
""",
    ),
    (
        "P1.13 — Webcam burst capture → session upload",
        M1,
        ["phase/1", "seat/product", "frontend", "demo-critical"],
        """## Product
PRODUCT § core: **Webcam / upload science session**.

## Tasks
- [ ] MediaRecorder 5–15s burst at 720p/30fps (scientific clip, not 60fps waste)
- [ ] Blob upload via same `POST /api/sessions` as file picker
- [ ] Browser permission UX + fallback to upload

## DoD
- [ ] Live demo can start from webcam without pre-recorded file
""",
    ),
    (
        "P1.14 — Spark Contributor routing + policy (META_USE_CONTRIBUTOR)",
        M1,
        ["phase/1", "seat/agent", "meta/spark", "meta/contributor"],
        """## Business logic
Cost routing (`META_TOOLING.md` §4): Contributor for volume observer loops; **not** for sensitive/user IP.

## Tasks
- [ ] `ModelRouter` switches model id suffix when `META_USE_CONTRIBUTOR=true`
- [ ] README + in-app note when contributor mode active
- [ ] Never route Wonder/Image/SAM through contributor

## DoD
- [ ] Log line shows contributor vs standard on Spark calls
""",
    ),
    (
        "P1.15 — Postgres schema migrations (full ARCHITECTURE §5 data model)",
        M1,
        ["phase/1", "seat/agent", "business-logic"],
        """## Tables (minimum)
Session, Observation, Track, Hypothesis, Experiment, ImaginationAudit, Tool, Law, Notebook

## Tasks
- [ ] Alembic or SQL migrations in repo
- [ ] Replace in-memory `store` when `DATABASE_URL` set (#15)
- [ ] Seed script for demo library optional

## DoD
- [ ] `docker compose up` applies migrations; session survives restart
""",
    ),
    (
        "P1.16 — E2E pipeline stage machine (orchestrator hardening)",
        M1,
        ["phase/1", "seat/agent", "business-logic", "demo-critical"],
        """## Business logic
`services/api/hypatia/pipeline.py` must match ARCHITECTURE §4 **exactly** — idempotent stages, resumable on failure.

## Tasks
- [ ] Split `run_full_pipeline` vs per-stage routes (`/observe`, `/measure`, …)
- [ ] Stage guards: cannot hypothesize before measure
- [ ] Partial re-run after experiment result
- [ ] Align `SessionStatus` enum with UI stepper (#52)

## DoD
- [ ] Contract test: happy path + fail-at-measure → resume
""",
    ),
    (
        "P2.8 — Accept law: held-out gates + POST /accept + UI commit beat",
        M2,
        ["phase/2", "seat/agent", "seat/science", "business-logic", "demo-critical"],
        """## Business logic
Step 7 ACCEPT LAW — **only** if gates pass (`ARCHITECTURE.md` §9).

## API
`POST /api/sessions/{id}/accept` → notebook + LawLibrary upsert

## UI
- [ ] "Commit law" disabled until held-out winner (#22)
- [ ] Show rivals eliminated + bootstrap CIs

## DoD
- [ ] Demo metric: pendulum g within ±10% (`PRODUCT.md` success table)
""",
    ),
    (
        "P2.9 — JSON schemas + API contract tests (SceneBrief, HypothesisBatch, NextTest)",
        M2,
        ["phase/2", "seat/agent", "meta/responses", "infra/ci"],
        """## Meta integration
Responses API `text.format: json_schema(...)` for agent contracts (`META_TOOLING.md` §3).

## Tasks
- [ ] Pydantic models == JSON Schema exported for Meta calls
- [ ] `tests/contract/` hits FastAPI routes with fixture payloads
- [ ] CI runs without `MODEL_API_KEY`

## DoD
- [ ] Breaking schema change fails CI
""",
    ),
    (
        "P2.10 — Observer narration in UI (Spark plain-language beat)",
        M2,
        ["phase/2", "seat/product", "frontend", "meta/spark"],
        """## Product
SceneBrief includes human-readable narration — show it beside masks (not chatbot sidebar theater).

## DoD
- [ ] Narration updates after observe stage; readable on mobile
""",
    ),
    (
        "P3.9 — Law library UI + self-improvement chart",
        M3,
        ["phase/3", "seat/product", "frontend", "business-logic", "demo-critical"],
        """## API + UI
- [ ] `GET /api/library/laws` (#35) rendered as cards
- [ ] Chart: sessions vs time-to-law (stretch: library hit rate)

## Demo beat
META_TOOLING §2 #4 + PRODUCT novelty #4 (memory)

## DoD
- [ ] Second pendulum session shows faster path or cached law hint
""",
    ),
    (
        "P3.10 — Voice realtime WebSocket ASR (stretch Meta surface)",
        M3,
        ["phase/3", "seat/product", "meta/voice"],
        """## Meta docs
`wss://api.meta.ai/v1/asr/realtime` (`META_TOOLING.md` §3.6)

## MVP first
File upload ASR on #32; this issue upgrades to **live mic stream** for demo wow.

## DoD
- [ ] Live transcript during experiment OR documented cut with file ASR fallback
""",
    ),
    (
        "P3.11 — Upload consent + ethics banner",
        M3,
        ["phase/3", "seat/product", "frontend"],
        """## ARCHITECTURE §11
Public demo: no sensitive lab IP without consent.

## DoD
- [ ] Checkbox/copy before upload/webcam; stored on session metadata
""",
    ),
    (
        "P4.11 — GitHub Actions: lint, fixture tests, Modal deploy on main",
        M4,
        ["phase/4", "infra/ci", "seat/agent"],
        """## DEPLOYMENT §8
- [ ] PR: pytest + ruff/eslint on `apps/web`
- [ ] `main`: `modal deploy` when secrets configured (#49)
- [ ] Never run live Meta in CI without opt-in

## DoD
- [ ] Badge in README
""",
    ),
    (
        "P4.12 — Demo reliability: live / hybrid / fixture operator controls",
        M4,
        ["phase/4", "seat/product", "frontend", "business-logic", "demo-critical"],
        """## RISKS.md runbook wired to UI
- [ ] Operator toggle: live → hybrid → fixture (verbal script in DEMO_SCRIPT)
- [ ] Hybrid = live Spark/Wonder + cached SAM tracks

## DoD
- [ ] Rehearsal: flip to fixture in <5s during mock demo
""",
    ),
    (
        "P4.13 — Marketing landing + README submission pack (Impact 30%)",
        M4,
        ["phase/4", "seat/product", "frontend"],
        """## Scope
- [ ] Hero HYPATIA brand on `/` (extend existing page.tsx)
- [ ] README: theme, track, models table, live URL, video, **built during hackathon** timeline
- [ ] India schools / Push the Frontier narrative (`PRODUCT.md`)

## DoD
- [ ] New contributor can run demo from README alone
""",
    ),
    (
        "P4.14 — Finals warm containers + health ping (Nov 4–9)",
        M4,
        ["phase/4", "infra/ci", "blocker"],
        """## DEPLOYMENT.md
`min_containers=1` on Modal API + Glimmer **Nov 4–9 only** (cost control).

## Tasks
- [ ] Document cron/ping (GitHub Action or UptimeRobot) hitting `/api/health`
- [ ] Vercel + Modal CORS recheck after warm

## DoD
- [ ] Cold start <3s p95 during judging window
""",
    ),
    (
        "P4.15 — API cost report script + session spend aggregation",
        M4,
        ["phase/4", "seat/science", "seat/agent"],
        """## Budget
~$150 credits (`HACKATHON_BRIEF.md` §6)

## Tasks
- [ ] `scripts/cost_report.py` aggregates logs (Spark tokens, SAM frames, Image count)
- [ ] README envelope vs actual

## DoD
- [ ] One sample report pasted in #40 evals issue
""",
    ),
    (
        "P4.16 — Wonder computer use: PhET sandbox harness (load-bearing if shipped)",
        M4,
        ["phase/4", "seat/agent", "meta/wonder", "meta/computer"],
        """## Note
Replaces thin P4.5 when you commit to stretch — **cut first** per RISKS kill order.

## Tasks
- [ ] Isolated browser VM; Wonder `computer` tool allowlist
- [ ] Demo: change pendulum length without human hands

## Depends
Meta computer use docs + Modal sandbox or local Docker
""",
    ),
]


def main() -> int:
    for name, color, desc in NEW_LABELS:
        create_label(name, color, desc)
    titles = existing_titles()
    n = 0
    for row in ISSUES:
        title = row[0]
        if title in titles:
            print(f"skip: {title}")
            continue
        create_issue(*row)
        print(f"created: {title}")
        n += 1
    print(f"Created {n} gap-fill issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
