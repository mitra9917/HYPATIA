# M3 ghost pipeline (Playbook #31–33 / issues #26–#28)

## Playbook #31 — Predictor (`predictor.py`)

- SHM `PendulumState` with `advance(Δt)` and `forward_polyline()` for ghost overlay
- `state_at_delta()` for mask hints at **t+Δ**
- `science.ghost_polyline()` delegates here

## Playbook #32 — Muse Image (`pipeline._imagine`)

- `POST /api/sessions/{id}/imagine` sets `ghost_frame_uri`
- `GET /api/sessions/{id}/imagination/0/frame.png`
- Live: Muse Image bytes saved; fixture: placeholder PNG
- `meta_calls` logs `image_spend_usd_est` (~$0.01) per generated frame

## Playbook #33 — SAM audit (`imagination_audit.py`)

- IoU + centroid error vs mask/trajectory at **t+Δ**
- Persisted on `ImaginationFrame`: `audit_iou`, `audit_centroid_m`, `mask_hint_bbox`

## Tests

```bash
export PYTHONPATH=services/api
pytest services/api/tests/test_m3_ghost.py services/api/tests/test_imagine_api.py -q
```
