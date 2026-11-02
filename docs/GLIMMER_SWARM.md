# Glimmer hypothesis swarm (P2.2 / issue #20)

Open-weight **Muse Glimmer** proposes rival functional forms; **SciPy held-out scoring** (`science.fit_rival_hypotheses`) decides the winner.

## Environment

| Variable | Values | Notes |
| --- | --- | --- |
| `GLIMMER_PROVIDER` | `stub` (default) | CPU rivals for CI and fixture replay |
| | `modal` | After `modal deploy services/api/modal_app.py` |
| | `baseten` | Requires `BASETEN_API_KEY` + `GLIMMER_BASETEN_URL` |
| | `fireworks` | Requires `FIREWORKS_API_KEY`; optional `GLIMMER_FIREWORKS_URL` |

See `.env.example` and [`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Code paths

- `hypatia/glimmer.py` — provider routing, `run_theorist_batch`, normalized candidate cards
- `hypatia/theorist.py` — `run_theorist_swarm_and_score` used in pipeline **hypothesize**
- `services/api/modal_app.py` — `glimmer_swarm` GPU placeholder (shared rival pool)
- `/api/health` — probes stub swarm when `GLIMMER_PROVIDER=stub`

## Local smoke

```bash
export PYTHONPATH=services/api
python scripts/smoke_glimmer.py
pytest services/api/tests/test_glimmer.py -q
```

## Demo

Use `GLIMMER_PROVIDER=modal` (or Baseten/Fireworks) before recording the demo video; keep `stub` in CI.

```bash
# Stub (CI default)
python3 scripts/smoke_glimmer.py

# After modal deploy
GLIMMER_PROVIDER=modal python3 scripts/smoke_glimmer.py

# With Wonder PI (needs MODEL_API_KEY)
bash scripts/smoke_judge_meta.sh
```

DoD: **≥3** pendulum rival forms per session; provider switch documented here and in README.
