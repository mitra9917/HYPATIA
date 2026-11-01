# First GitHub issues to open (after this docs PR merges)

Copy into GitHub Issues. Milestone: **M1 — Perception E2E**. Labels suggested in BUILD_PLAN.

---

### Issue: Scaffold monorepo (api + web + compose)

**Phase:** P1.1  
**Seat:** product  
**DoD:** `docker compose up` starts Postgres; placeholder FastAPI `/api/health` and Next.js hello page; `.env.example` wired.

---

### Issue: Meta Model API client + smoke script

**Phase:** P1.2  
**Seat:** agent  
**DoD:** `scripts/smoke_meta_api.py` calls Spark + SAM (or skips cleanly without key); shared client with logging of model/tokens/latency.

---

### Issue: Observer agent (Spark video → SceneBrief)

**Phase:** P1.3  
**Depends:** P1.2  
**DoD:** Given a pendulum clip, returns JSON with objects + `sam_prompts`; fixture saved under `data/fixtures/`.

---

### Issue: SAM measurer + calibration → trajectories

**Phase:** P1.4 + P1.5  
**Seat:** vision  
**DoD:** Masks overlay data + angle/length time series in metres; unit tests for scale math.

---

### Issue: Session API + SSE + UI upload/overlay/chart

**Phase:** P1.6 + P1.7  
**Seat:** agent + product  
**DoD:** Browser upload runs observe→measure; live progress; 30s GIF attached to issue.

---

### Issue: Collect test videos + SOURCES.md

**Phase:** P1.8  
**Seat:** science  
**DoD:** ≥8 desk clips listed in `data/videos/SOURCES.md` with rights; stored per REPO_STRUCTURE (Release or external link if large).

---

## After M1

Open M2 issues from `docs/BUILD_PLAN.md` Phase 2 (PySR, Glimmer swarm, Wonder PI, held-out gate, hypothesis UI).
