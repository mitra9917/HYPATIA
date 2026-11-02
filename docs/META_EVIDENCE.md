# Meta tooling evidence pack (Playbook #60 / issue #40)

Judges scan this table — it mirrors [`META_TOOLING.md`](./META_TOOLING.md) §5 with **real repo paths** and demo timestamps from [`demo/DEMO_SCRIPT.md`](../demo/DEMO_SCRIPT.md).

| Capability | Meta tool | Module / route | Demo timestamp | Verified |
| --- | --- | --- | --- | --- |
| Open-vocab measure | SAM 3.1 | `services/api/hypatia/measurer.py` | 0:15–0:45 | fixture + live hooks |
| Scene understanding | Muse Spark 1.3 | `services/api/hypatia/observer.py` | 0:00–0:15 | fixture + live |
| Rival theories + PI plan | Muse Wonder 1.0 | `services/api/hypatia/pi.py`, `pi_tools.py` | 0:45–1:15 | fixture plans |
| Ghost imagination | Muse Image 1.0 | `services/api/hypatia/pipeline.py` `_imagine` | 1:15–1:45 | fixture PNG + geometric fallback |
| SAM grades ghost | SAM 3.1 audit | `imagination` audit_error_m on session | 1:15–1:45 | fixture |
| Hypothesis swarm | Glimmer (stub/Modal) | `services/api/hypatia/glimmer.py` | 0:45–1:15 | stub in CI |
| Voice hands-free | Muse Voice Transcribe | `services/api/hypatia/voice.py`, `/api/voice/turn` | experiment panel | fixture stub |
| Toolsmith instrument | Wonder + sandbox | `services/api/hypatia/toolsmith/`, `POST /api/toolsmith/test-promoted` | 1:45–2:15 | fixture track test |
| Cell domain | Spark fixture | `data/fixtures/observer_cells.json` | 1:45–2:15 | `cells-notebook.md` |
| VERITAS integrity | Spark + measure stack | `services/api/hypatia/veritas.py` | 2:15–2:35 | fixture fake fall |
| Built with Muse Code | process | B-roll in `demo/` | credits | narrative |

Machine-readable copy for parsers: [`meta_evidence.json`](../meta_evidence.json).

**Live Meta smoke (opt-in):** `python scripts/smoke_meta_api.py` with `MODEL_API_KEY` in `.env`.
