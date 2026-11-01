# Repository Structure

Target layout for the full-stack HYPATIA monorepo. Phase 1 may start with the **simplified layout** at the bottom and grow into packages.

## Full target

```text
.
├── AGENTS.md                 # conventions for coding agents
├── README.md                 # product + links + evals + built-during
├── render.yaml               # Render Blueprint
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── apps/
│   └── web/                  # Next.js App Router UI
│       ├── package.json
│       ├── app/
│       ├── components/
│       │   ├── MaskOverlay.tsx
│       │   ├── GhostOverlay.tsx
│       │   ├── HypothesisCards.tsx
│       │   ├── ExperimentPrompt.tsx
│       │   └── TrajectoryChart.tsx
│       └── lib/api.ts
├── services/
│   └── api/                  # FastAPI
│       ├── requirements.txt
│       ├── pyproject.toml
│       └── hypatia/
│           ├── app.py
│           ├── routes/
│           ├── db/
│           └── workers/
├── packages/                 # shared Python modules (editable installs)
│   ├── meta/                 # Model API clients, ModelRouter
│   ├── agents/               # PI, Observer, ExperimentDesigner
│   ├── vision/               # SAM, calibration, trajectories
│   ├── science/              # PySR, scoring, VERITAS, priors
│   ├── imagination/          # Muse Image ghost + audit
│   └── toolsmith/            # sandbox + library
├── data/
│   ├── videos/               # clips + SOURCES.md
│   └── fixtures/             # cached API / session replays
├── evals/
│   ├── run.py
│   ├── suites/
│   └── results/
├── demo/
│   ├── DEMO_SCRIPT.md
│   └── exports/              # large binaries gitignored or Release assets
├── docs/                     # planning & architecture (this folder)
└── scripts/
    ├── smoke_meta_api.py
    ├── warm_meta_files.py
    └── seed_library.py
```

## Simplified Phase-1 layout (acceptable)

If packaging slows us down:

```text
.
├── apps/web/
├── services/api/hypatia/
│   ├── app.py
│   ├── meta_client.py
│   ├── observer.py
│   ├── measurer.py
│   ├── pi.py
│   ├── science.py
│   ├── imagination.py
│   └── ...
├── data/
├── demo/
├── docs/
├── evals/
├── scripts/
├── docker-compose.yml
└── render.yaml
```

Promote to `packages/` only when imports get messy.

## Naming

- Product name: **HYPATIA** (all caps in brand surfaces)
- Package/module: `hypatia`
- API prefix: `/api/...`
- Branches: `cursor/<descriptive>-db99`

## What lands in git vs not

| In git | Not in git |
| --- | --- |
| Docs, code, small fixtures JSON | `.env`, raw huge MP4s (use GitHub Releases / Drive + SOURCES) |
| Tiny sample frames for CI | API keys, Modal tokens |
| Eval result markdown summaries | `node_modules/`, `.venv/` |
