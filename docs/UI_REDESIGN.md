# HYPATIA UI redesign

Multi-page Next.js App Router layout replacing the single long scrolling lab page. Goal: minimal premium aesthetic, full API coverage in fixture mode, KaTeX for laws, deduplicated law library.

## Information architecture

| Route | Purpose |
| --- | --- |
| `/` | Landing: pitch, health stats, quick links |
| `/lab` | Guided run: consent, upload/webcam burst, stepper, observe/measure/rivals/gates |
| `/session/[id]` | Deep dive: tracks, ghost audit, leaderboard, experiment, voice, PI plans, commit law |
| `/sessions` | Recent browser sessions + accepted laws (no list-sessions API) |
| `/library` | Law library: search, domain grouping, dedupe by normalized LaTeX |
| `/notebook` | Notebook markdown preview + download links |
| `/settings` | Ops mode, fixture/contributor banners, consent, health, VERITAS, Toolsmith, cells domain |
| `/about` | Hackathon alignment, Meta toolkit table, doc links |

## Design tokens (`app/globals.css`)

- **Background:** `#f7f6f3` (warm paper)
- **Surface:** `#ffffff` with soft shadow
- **Ink:** `#141414` / muted `#5c5c5c`
- **Accent:** `#1a5c52` (restrained teal)
- **Typography:** Instrument Serif (display), Inter (UI), JetBrains Mono (meta)
- **Radius:** 12px panels, pill buttons

Legacy CSS variables (`--signal`, `--law`, etc.) remain as aliases so canvas/overlay components keep working.

## Components

| Component | Role |
| --- | --- |
| `shell/AppShell`, `SiteNav`, `PageHeader` | Global chrome |
| `KatexMath` | Render `form_latex` / law strings |
| `HypothesisLeaderboard` | Held-out score bars |
| `AcceptGatePanel` | Scoring gate checklist |
| `PipelineStepper`, `TrackOverlay`, `GhostCanvas`, … | Unchanged science visuals, light shell |

## Data wiring

- All calls go through `lib/api.ts` (unchanged contracts + VERITAS, Toolsmith, tools library, cells session create).
- `lib/lab-run.ts` centralizes fixture demo, SSE progress, recent session IDs in `localStorage`.
- `lib/laws.ts` deduplicates `GET /api/library/laws` for the library page.

## Fixture demo

```bash
./scripts/run_api_local.sh
cd apps/web && cp .env.local.example .env.local && npm run dev
```

Open `/lab?demo=1` or **Run desk pendulum demo** — runs `POST /api/sessions` + `POST .../run` with SSE.

## Not surfaced (API / product limits)

| Feature | Reason |
| --- | --- |
| Global session list | No `GET /api/sessions`; UI uses recent IDs + law library session_ids |
| Live Meta model picker | Model IDs are server env only |
| `GET /api/health?meta_ping=1` | Slow probe; not exposed in UI (health card uses default health) |
| Full notebook editor | Download-only; markdown preview is read-only |
| Computer-use / Modal deploy controls | Backend/infra only |
| Real voice transcription | Scaffold; UI shows fixture/WebSocket fallback |
| PySR live path | Optional backend import; UI shows SciPy/Glimmer rivals only |

## Screenshots

Captured at 1440×900 desktop and 390×844 mobile after a fixture demo run (see PR body for artifact paths).
