# HYPATIA

**The camera that does science.**

Point any camera at anything that moves. HYPATIA finds the law behind it, proves the law by predicting the future, then tells you which experiment to run next.

> We gave Meta's models a camera and the scientific method. It rediscovered Galileo on my desk in 90 seconds.

Built for the **Meta Global AI Developer Hackathon** — **Indie track** · **Push the Frontier**.

| | |
| --- | --- |
| Status | Full-stack scaffold live (fixture E2E + Meta live hooks) |
| Deadline | **Nov 4, 2026, 9:00 PM ET** / **Nov 5, 7:30 AM IST** |
| Deploy priority | **Meta Model API → Modal / Baseten / Fireworks → AWS** |

---

## Quick start (local)

```bash
cp .env.example .env          # optional; fixture mode needs no Meta key
bash scripts/run_api_local.sh # terminal 1 — API on :8000
cd apps/web && npm install && npm run dev   # terminal 2 — UI on :3000
bash scripts/smoke_health.sh  # pretty-print /api/health (10s demo check)
```

**Docker full stack** (Postgres + API + web): `docker compose up --build` → http://localhost:3000

### Live Meta mode

1. Copy `.env.example` → `.env` and set `MODEL_API_KEY`
2. Set `FIXTURE_MODE=false`
3. Restart API; `/api/health` should show `"meta": true`

```bash
python scripts/smoke_meta_api.py
```

### Deploy (Meta partners first)

```bash
# Modal (hackathon partner — primary)
modal secret create hypatia-secrets MODEL_API_KEY=... 
modal volume create hypatia-weights
modal deploy services/api/modal_app.py
```

Open-weight failover: Baseten or Fireworks (`GLIMMER_PROVIDER=baseten|fireworks`).  
Storage / compute backup: **AWS S3** (+ ECS/EC2 if Modal unavailable). See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

---

## What it does

1. **Observe** — Muse Spark scene brief + SAM prompts  
2. **Measure** — SAM 3.1 / calibrated trajectories → metres  
3. **Hypothesise** — rival laws; held-out scoring (maths decides)  
4. **Imagine** — Muse Image or geometric ghost; audit error  
5. **Experiment** — highest-information next test  
6. **Notebook** — accepted law + params + error bars  

---

## Meta models

| Model | Job |
| --- | --- |
| Muse Spark 1.3 | Observer |
| Muse Wonder | Principal Investigator / experiment phrasing |
| Muse Image | Predicted-frame imagination |
| SAM 3.1 | Measurement + audit probe |
| Muse Glimmer (partners) | Hypothesis swarm on Modal/Baseten/Fireworks |
| Muse Voice Transcribe | Hands-free (wired next) |
| Muse Code | Build acceleration |

---

## Docs

Start at [`docs/INDEX.md`](docs/INDEX.md). Key pages: product, architecture, Meta tooling, **deployment**, win strategy, build plan, demo script.

---

## Built during the hackathon

Event window **Oct 26 – Nov 4, 2026 (ET)**. This public repo is the submission surface; commit history marks new work.

---

## License

MIT (intended). Third-party videos must be listed in `data/videos/SOURCES.md`.
