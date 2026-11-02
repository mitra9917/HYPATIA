# Wonder PI orchestration (P2.3 / issue #21)

Muse Wonder plans each major pipeline phase once; tool execution stays in Python (Glimmer, PySR/SciPy, library stub).

## Phases

| Phase | PI tools (typical) | Delegates to |
| --- | --- | --- |
| observe | `delegate_spark` | Observer (Spark) |
| measure | `delegate_sam` | Measurer (SAM) |
| hypothesize | `spawn_theorist`, `run_pysr`, `library_search` | Glimmer + symbolic fitter + law library |
| experiment | `library_search` | Prior laws + maths-chosen proposal |

## Continuity

- Session fields: `pi_response_id`, `pi_plans`
- Each live Wonder plan passes `previous_response_id` from the prior PI call
- Fixture / CI uses `fixture_pi_plan()` — **no Wonder HTTP**

## API

`POST /api/sessions/{id}/hypothesize` returns `RunResponse` with hypotheses sorted by held-out score (winner first).

## Tests

```bash
export PYTHONPATH=services/api
pytest services/api/tests/test_pi.py services/api/tests/test_orchestrator.py -q
```
