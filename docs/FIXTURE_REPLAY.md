# Fixture replay (Playbook #23 / issue #18)

## Replay mode (`FIXTURE_MODE=true`)

The API serves **Observer** (`data/fixtures/observer_pendulum.json`) and **SAM tracks** (`data/fixtures/tracks/*`) without calling Meta. Health reports `fixture_mode: true` and `replay_mode: true`. The lab UI shows an orange **Replay mode** banner.

## Recording a new slice (live Meta)

1. Set `FIXTURE_MODE=false`, `MODEL_API_KEY=…`, and `FIXTURE_RECORD=true` in `.env`.
2. Run observe + measure on a pendulum session (UI or API), **or**:

```bash
export PYTHONPATH=services/api
python3 scripts/record_fixture_slice.py
# optional: --session-id <uuid> after POST /api/sessions with upload
```

3. Canonical outputs (when `promote_canonical=True`):
   - `data/fixtures/observer_pendulum.json`
   - `data/fixtures/tracks/pendulum_bob_default.json`
   - `data/fixtures/sam/pendulum_boxes.json` (when SAM masks decoded)

Commit updated fixtures only when you have rights to the media/responses.

## Demo reliability

Judges and CI should keep `FIXTURE_MODE=true`. Live capture is for maintainers refreshing fixtures after a verified Meta smoke.
