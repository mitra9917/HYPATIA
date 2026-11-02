# Lab UI demo capture (P1.7 / issue #16)

## Fixture mode (judges offline)

1. API: `FIXTURE_MODE=true` (default in `.env.example`).
2. Web: `./scripts/run_api_local.sh` + `npm run dev` in `apps/web`.
3. Click **Run desk pendulum demo** — no upload or Meta key required.
4. Confirm: replay banner, stepper, SAM mask scrubber, angle vs time chart.

## 30s GIF for PR

Record a screen capture (~30s) showing:

- Upload or **Webcam burst** → stepper advancing
- Measurer panel: mask scrubber + trajectory chart
- Ghost / law card at end (fixture run is fine)

Save as `demo/lab-ui-perception.gif` and link in the PR body (GitHub drag-and-drop).

```bash
# macOS example (QuickTime or Screen Recording → convert)
# ffmpeg -i lab-ui.mov -vf "fps=12,scale=1280:-1" -t 30 demo/lab-ui-perception.gif
```

## Live webcam

Requires HTTPS or `localhost`, camera permission, and `FIXTURE_MODE=false` + Meta key for full live pipeline. Webcam burst still creates an upload session for observe/measure.
