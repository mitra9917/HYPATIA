#!/usr/bin/env python3
"""Create remaining HYPATIA GitHub issues (skip if title already exists)."""
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


def milestone_map() -> dict[str, int]:
    ms = gh_json("api", f"repos/{REPO}/milestones?state=open")
    return {m["title"]: m["number"] for m in (ms or [])}


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


ISSUES: list[tuple[str, str, list[str], str]] = [
    (
        "[INTEGRATION] Postgres (Neon/Supabase) + optional S3/R2 for media",
        "M0 — Docs & integration spine",
        ["integration-human", "phase/0", "phase/4"],
        """## Why
Durable sessions, laws, notebooks — not ephemeral Modal disk alone (AGENTS.md non-negotiable #7).

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
""",
    ),
    (
        "[INTEGRATION] Vercel project for Next.js lab UI",
        "M0 — Docs & integration spine",
        ["integration-human", "seat/product", "phase/0", "phase/4"],
        """## Why
AGENTS.md default: **Vercel (web) + Modal (API)**. Judges need one stable demo URL.

## What YOU must do
1. Import GitHub repo `mitra9917/HYPATIA` in Vercel — root directory **`apps/web`**.
2. Set environment variables in Vercel project settings:
   - `API_ORIGIN` = your Modal ASGI public URL (after deploy)
   - Any `NEXT_PUBLIC_*` vars the web app requires (see P1.7 / P4.6)
3. Enable preview deployments on PRs; production branch `main`.

## When
After first working local UI (P1.7); **required** before submission (M4).

## DoD
- [ ] Preview URL loads lab UI
- [ ] Production URL listed in README (P4.9)
""",
    ),
    (
        "[INTEGRATION] Muse Code — process evidence for judges",
        "M0 — Docs & integration spine",
        ["integration-human", "meta/code", "phase/0", "phase/4"],
        """## Why
Hackathon stack lists **Muse Code** as the coding agent. Judges reward authentic "built with Meta" process.

## What YOU must do
1. Use Muse Code for at least one vertical slice PR.
2. Record **10–15s B-roll** of Muse Code committing/running tests (no secrets on screen).
3. Add clip to demo folder or unlisted drive; link in README "Built during hackathon" section.

## When
During Phases 1–3 coding; finalize before **P4.8 demo video**.

## DoD
- [ ] B-roll file linked in issue comment
- [ ] README mentions Muse Code in tooling table (docs/META_TOOLING.md §6)
""",
    ),
    (
        "[INTEGRATION] Muse Spark Open (optional self-host fallback)",
        "M0 — Docs & integration spine",
        ["integration-human", "meta/spark", "phase/0"],
        """## Why
Hackathon allows **Muse Spark Open** as open-weight multimodal fallback if API rate/cost bites.

## What YOU must do (optional — only if needed)
1. If Modal/Baseten/Fireworks offers Spark Open weights, deploy an endpoint.
2. Document env var in `.env.example` when P3.8 hybrid routing lands.
3. Keep **API Spark as primary** for judging clarity.

## When
Only if live demos hit rate limits during M3/M4.

## DoD
- [ ] Either skipped with comment "API only" OR fallback URL documented
""",
    ),
    (
        "P0.11 — Verify docs spine + close planning milestone",
        "M0 — Docs & integration spine",
        ["phase/0", "seat/product"],
        """## Context
Phase 0 docs should already exist under `docs/` (see `docs/INDEX.md`).

## Tasks
- [ ] Read order: HACKATHON_BRIEF → PRODUCT → ARCHITECTURE → META_TOOLING → BUILD_PLAN
- [ ] Confirm theme: **Push the Frontier**; track: **Indie**
- [ ] Mark integration issues complete as YOU finish each setup
- [ ] Attach screenshot of repo docs tree in comment

## DoD
All `[INTEGRATION]` issues either closed or have explicit blocker + OH plan.
""",
    ),
]

# Append P1–P4 from compact definitions
def p1_p4():
    M1 = "M1 — Perception E2E"
    M2 = "M2 — First law"
    M3 = "M3 — Ghost & experiment"
    M4 = "M4 — Deploy, evals, submit"
    items = [
        ("P1.1 — Monorepo scaffold hardening (api + web + compose)", M1, ["phase/1", "seat/product", "demo-critical"],
         "See scripts/create_github_issues.sh body in BUILD_PLAN P1.1 — docker compose, health, README quickstart."),
    ]
    return items


# Full issue list inlined (remainder from failed bash script)
def all_remaining() -> list[tuple[str, str, list[str], str]]:
    M0 = "M0 — Docs & integration spine"
    M1 = "M1 — Perception E2E"
    M2 = "M2 — First law"
    M3 = "M3 — Ghost & experiment"
    M4 = "M4 — Deploy, evals, submit"
    base = list(ISSUES)
    base.extend([
        ("P1.1 — Monorepo scaffold hardening (api + web + compose)", M1, ["phase/1", "seat/product", "demo-critical"],
"""## Goal
Reliable local full stack for every developer/agent.

## Scope
- `docker compose up` → Postgres + API + web (or documented hybrid)
- `/api/health` returns model router info + `fixture_mode`
- `.env.example` documents every Meta + partner var

## DoD
- [ ] README quickstart ≤5 commands
- [ ] Demo note: show health JSON in 10s
"""),
        ("P1.2 — Meta Model API client (Responses + Files + logging)", M1,
         ["phase/1", "seat/agent", "meta/spark", "meta/sam", "blocker", "demo-critical"],
"""## Goal
Single ModelRouter / meta_client for all hosted Meta calls with logging (model, tokens/frames, latency_ms, session_id).

## Meta models
Spark, SAM, Wonder (smoke), Image, Voice (optional in smoke)

## DoD
- [ ] scripts/smoke_meta_api.py live + fixture paths
- [ ] Depends: close [INTEGRATION] Meta Model API key (#2)
"""),
        ("P1.3 — Observer agent (Spark video → SceneBrief JSON)", M1,
         ["phase/1", "seat/agent", "meta/spark", "demo-critical"],
"""## Goal
SceneBrief with sam_prompts[] for Measurer. POST /api/sessions/{id}/observe.

## DoD
- [ ] Fixture under data/fixtures/
- [ ] Live muse-spark-1.3 + video file_id
"""),
        ("P1.4 — SAM 3.1 video measurer + meta_sam_parser decode", M1,
         ["phase/1", "seat/vision", "meta/sam", "demo-critical"],
"""## Goal
SAM 3.1 video track per sam_prompt; cache tracks; 10–15 fps clips.

## DoD
- [ ] Masks to frontend; log frame cost estimate
"""),
        ("P1.5 — Calibration + SI trajectories (A4 / coin + OpenCV)", M1,
         ["phase/1", "seat/vision", "seat/science", "demo-critical"],
"""## Goal
Pixel tracks → metres, radians, seconds. Unit tests without Meta.

## DoD
- [ ] Pendulum angle series + CSV export
"""),
        ("P1.6 — Session API + Postgres persistence + SSE progress", M1,
         ["phase/1", "seat/agent", "demo-critical"],
"""## Endpoints
POST /api/sessions, GET /api/sessions/{id}, GET /api/sessions/{id}/events (SSE)

## DoD
- [ ] Stages: observe → measure
- [ ] Depends: INTEGRATION Postgres
"""),
        ("P1.7 — Lab UI: upload/webcam, mask overlay, trajectory chart", M1,
         ["phase/1", "seat/product", "demo-critical"],
"""## DoD
- [ ] 30s GIF on PR
- [ ] Fixture mode for offline judges
"""),
        ("P1.8 — Test video corpus + SOURCES.md (rights-safe)", M1, ["phase/1", "seat/science"],
"""## DoD
- [ ] ≥8 clips in data/videos/SOURCES.md with licenses
"""),
        ("P1.9 — Fixture recorder + replay mode banner", M1, ["phase/1", "seat/agent", "demo-critical"],
"""## DoD
- [ ] Record observer + SAM slice; UI banner when FIXTURE_MODE=true
"""),
        ("P2.1 — Equation DSL + PySR / SciPy symbolic fitter", M2, ["phase/2", "seat/science", "demo-critical"],
"""## DoD
- [ ] Recover g on synthetic + fixture pendulum data
"""),
        ("P2.2 — Glimmer swarm adapter (theorist batch + CPU stub)", M2,
         ["phase/2", "seat/agent", "meta/glimmer", "demo-critical"],
"""## DoD
- [ ] ≥3 rival forms; GLIMMER_PROVIDER documented
- [ ] Depends: INTEGRATION Glimmer (#4) before demo
"""),
        ("P2.3 — Wonder PI orchestration (plan → measure → hypothesize)", M2,
         ["phase/2", "seat/agent", "meta/wonder", "demo-critical"],
"""## DoD
- [ ] POST /api/sessions/{id}/hypothesize ranked rivals
- [ ] Wonder once per phase, not per keystroke
"""),
        ("P2.4 — Held-out scoring gate + bootstrap confidence intervals", M2,
         ["phase/2", "seat/science", "demo-critical"],
"""## DoD
- [ ] Unit tests; UI train vs held-out scores
"""),
        ("P2.5 — UI hypothesis cards + rival comparison", M2, ["phase/2", "seat/product", "demo-critical"],
"""## DoD
- [ ] Demo: T=2π√(L/g), g≈9.7±0.4
"""),
        ("P2.6 — Lab notebook markdown export", M2, ["phase/2", "seat/product"],
"""## DoD
- [ ] Download notebook with law, CSV, models used
"""),
        ("P2.7 — Eval harness v0 (≥5 clips metrics)", M2, ["phase/2", "seat/science"],
"""## See docs/EVALS.md — table for README P4.7
"""),
        ("P3.1 — Predictor (kinematic / ODE forward simulation)", M3, ["phase/3", "seat/science", "demo-critical"],
"""## DoD
- [ ] state(t+Δ) for ghost pipeline
"""),
        ("P3.2 — Muse Image ghost pipeline + mask hints", M3,
         ["phase/3", "seat/vision", "meta/image", "demo-critical"],
"""## DoD
- [ ] POST /api/sessions/{id}/imagine; log image spend
"""),
        ("P3.3 — SAM imagination audit (predicted vs real frame)", M3,
         ["phase/3", "seat/vision", "meta/sam", "demo-critical"],
"""## DoD
- [ ] IoU/centroid error meter — "SAM grades Muse Image"
"""),
        ("P3.4 — Geometric ghost fallback renderer", M3, ["phase/3", "seat/vision", "demo-critical"],
"""## DoD
- [ ] Auto-fallback if Muse Image fails; docs/RISKS.md updated
"""),
        ("P3.5 — Experiment Designer (information gain over rivals)", M3, ["phase/3", "seat/agent", "meta/wonder"],
"""## DoD
- [ ] POST /api/sessions/{id}/experiment/propose — double string length beat
"""),
        ("P3.6 — Human-in-the-loop experiment UI + result ingestion", M3,
         ["phase/3", "seat/product", "demo-critical"],
"""## DoD
- [ ] POST /api/sessions/{id}/experiment/result
"""),
        ("P3.7 — Voice loop (Muse Voice Transcribe → PI reply)", M3,
         ["phase/3", "seat/product", "meta/voice", "demo-critical"],
"""## DoD
- [ ] POST /api/voice/turn + mic UI
"""),
        ("P3.8 — Hybrid fixture/live mode switch + ops banner", M3, ["phase/3", "seat/agent"],
"""## DoD
- [ ] Flip live ↔ fixtures without redeploy
"""),
        ("P4.1 — Toolsmith sandbox (Modal) + unit test on frames", M4, ["phase/4", "seat/agent", "meta/wonder"],
"""## DoD
- [ ] One promoted tool; Modal sandbox no host network
"""),
        ("P4.2 — Law + tool library persistence + API", M4, ["phase/4", "seat/agent", "demo-critical"],
"""## DoD
- [ ] GET /api/library/laws; second session faster
"""),
        ("P4.3 — Cell time-lapse domain (reuse engine)", M4,
         ["phase/4", "seat/science", "seat/vision", "meta/spark"],
"""## DoD
- [ ] Logistic growth notebook export
"""),
        ("P4.4 — VERITAS module (AI fall clip physics break)", M4,
         ["phase/4", "seat/science", "meta/spark", "meta/sam"],
"""## DoD
- [ ] Verdict card on fake physics clip
"""),
        ("P4.5 — [STRETCH] Wonder computer use vs PhET pendulum", M4, ["phase/4", "seat/agent", "meta/wonder"],
"""## Cut last — dev.meta.ai/docs/computer-use
"""),
        ("P4.6 — Production deploy: Modal API + Vercel web + health/warm", M4,
         ["phase/4", "seat/product", "demo-critical", "blocker"],
"""## DoD
- [ ] Public URL; CORS; modal deploy + Vercel API_ORIGIN
- [ ] Depends: INTEGRATION Modal (#3) + Vercel + Postgres as used
"""),
        ("P4.7 — Evals table + Meta tooling evidence in README", M4,
         ["phase/4", "seat/science", "meta/spark", "meta/wonder", "meta/sam", "meta/image", "meta/glimmer", "meta/voice"],
"""## DoD
- [ ] META_TOOLING.md §5 table filled with paths + timestamps
"""),
        ("P4.8 — Record and edit 3:00 demo video", M4, ["phase/4", "seat/product", "demo-critical", "blocker"],
"""## DoD
- [ ] demo/DEMO_SCRIPT.md beats + Muse Code B-roll
"""),
        ("P4.9 — Submission package (form, links, open source checklist)", M4, ["phase/4", "seat/product", "blocker"],
"""## Deadline
Nov 4, 9:00 PM ET (Nov 5 7:30 AM IST) — see HACKATHON_BRIEF.md §7
"""),
        ("P4.10 — Public social clip + repo polish", M4, ["phase/4", "seat/product"],
"""## DoD
- [ ] 30–60s clip linked in README
"""),
    ])
    return base


def main() -> int:
    titles = existing_titles()
    ms = milestone_map()
    created = 0
    for title, milestone_title, labels, body in all_remaining():
        if title in titles:
            print(f"skip exists: {title}")
            continue
        if milestone_title not in ms:
            print(f"missing milestone: {milestone_title}", file=sys.stderr)
            return 1
        create_issue(title, milestone_title, labels, body)
        print(f"created: {title}")
        created += 1
    print(f"Done. Created {created} issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
