# Video sources & rights (P1.8 / Playbook #28, issue #17)

Every clip used in demos, evals, or marketing must be listed here. **Missing or unclear rights = disqualification risk.**

Large binaries live under `data/videos/` (gitignored `*.mp4` / `*.mov` / `*.webm`) or `demo/` — this file is the **source of truth** for licenses.

| ID | File / location | Origin | License / permission | Used in |
| --- | --- | --- | --- | --- |
| `broll-meta` | [`demo/muse-code-broll.mp4`](../../demo/muse-code-broll.mp4) | Team-produced hackathon B-roll | **Team-owned** (MITra9917 / HYPATIA repo) | Marketing, README, process evidence |
| `pendulum-desk-01` | `data/videos/desk_pendulum_charger.mp4` | Own desk recording (phone tripod) | **Team-owned** | 3-min demo, live Meta observe |
| `pendulum-fixture` | `data/fixtures/` + `observer_pendulum.json` | Recorded/hybrid fixture slice (no full video in git) | **Team-owned** responses | `FIXTURE_MODE=true`, CI, judges offline |
| `ramp-desk-01` | `data/videos/desk_ramp_cart.mp4` | Own desk recording | **Team-owned** | Eval: \(s=\frac12 at^2\) |
| `freefall-desk-01` | `data/videos/desk_free_fall_ball.mp4` | Own desk recording | **Team-owned** | Eval: vertical motion |
| `coin-calib-01` | `data/videos/desk_coin_calibration.mp4` | Own desk recording (coin + A4) | **Team-owned** | Calibration / measure stage tests |
| `cells-placeholder` | [Wikimedia: cell division timelapse (example)](https://commons.wikimedia.org/wiki/Category:Time-lapse_videos_of_cells) — pick one CC clip and cite exact file page | Public scientific clip | **CC BY-SA** (attribute author + link in PR) | Cross-domain demo placeholder |
| `ai-fake-physics-01` | `data/videos/ai_fake_freefall.mp4` | Muse Image / synthetic “wrong physics” clip | **Team-owned** generation | VERITAS / fake-physics verdict card (P2+) |
| `webcam-burst` | Lab UI capture → `data/media/{session}_*.webm` | Operator webcam burst (5–15s) | **Team-owned** (operator is team) | Live demo without pre-recorded file |
| `pendulum-ref-cc0` | [Wikimedia Commons search: pendulum slow motion](https://commons.wikimedia.org/w/index.php?search=pendulum+slow+motion&title=Special:MediaSearch) | Optional reference / style only | **Verify CC0/CC BY on file page** before use | Optional comparison, not shipped in repo |

## Minimum corpus (DoD)

- **≥8 rows** in the table above (excluding header).
- Before submission: drop real files into `data/videos/` for team-owned rows **or** replace external rows with exact URLs + attribution.

## Recording checklist (desk)

1. 720p or 1080p, **30fps**, 5–15s, bright light, high-contrast bob/ramp.
2. Include **A4 sheet** or coin in frame when testing calibration.
3. Copy file to `data/videos/` with the name in this table.
4. Update the row if filename or license changes.

## Rules

1. Prefer **team-recorded** desk experiments.
2. Public clips only with **clear license** (CC0, CC BY, public domain) and **attribution** in this file.
3. No scraped social media of strangers without permission.
4. No copyrighted movie/TV/sports footage.

## Verify locally

```bash
./scripts/verify_video_corpus.sh
```
