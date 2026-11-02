# Demo reliability — operator controls (Playbook #56 / issue #64)

Wired to **`OpsModeBanner`** on the lab home page and **`POST /api/ops/mode`**.

## Rehearsal script (<5s fixture flip)

1. Start API: `./scripts/run_api_local.sh`
2. Open `http://localhost:3000`
3. Confirm **Ops mode** shows `fixture` and **Run desk pendulum demo** completes (~30–90s)
4. If Meta rate-limits during live rehearsal: click **fixture** (already active) or switch **hybrid** when `MODEL_API_KEY` is set
5. Verbal line (from `demo/DEMO_SCRIPT.md`): *“Flipping to fixture replay so judges always see the law card.”*

## Hybrid semantics

- **fixture** — replay fixtures for Observer/SAM tracks (see `FIXTURE_MODE` + ops override)
- **hybrid** — live Spark/Wonder where enabled; SAM tracks may fall back to cached fixtures (`runtime_ops.hybrid_fallback_enabled`)
- **live** — Meta paths end-to-end (requires key)

## Runbook

See `docs/RISKS.md` kill order if the demo overruns time.
