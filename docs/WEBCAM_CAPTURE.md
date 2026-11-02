# Webcam burst capture (Playbook #26 / issue #53)

## User flow

1. Open lab UI on **localhost** (camera APIs require secure context).
2. Adjust **Burst length** (5–15 seconds, default 8) — matches scientific clip length, not 60fps waste.
3. Click **Start webcam burst** → allow camera → live preview while recording.
4. WebM uploads via **`POST /api/sessions`** with `source_type=webcam` (same route as file picker).
5. Pipeline runs observe → measure → … with stepper/SSE progress.

## Permission denied

UI shows a short message and points to **Upload clip** — no dead end.

## API

```bash
curl -F "file=@burst.webm;type=video/webm" -F "source_type=webcam" \
  http://127.0.0.1:8000/api/sessions
```

Session JSON includes `"source_type": "webcam"`.

## Live vs fixture

- **Fixture mode:** pipeline still replays fixtures for Meta stages; webcam proves capture + upload path for demos.
- **Live mode:** set `FIXTURE_MODE=false` + `MODEL_API_KEY` so Observer/SAM run on the recorded burst.

See also `docs/LAB_UI_DEMO.md`.
