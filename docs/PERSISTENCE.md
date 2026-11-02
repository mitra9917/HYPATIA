# Postgres persistence — Playbook #21 / issue #55

## Schema

SQL migrations live in `services/api/migrations/`. Initial migration `001_architecture_v5.sql` creates ARCHITECTURE §5 tables:

Session, Observation, Track, Hypothesis, Experiment, ImaginationAudit, Tool, Law, Notebook

## Runtime

| `DATABASE_URL` | Store |
| --- | --- |
| unset | in-memory (`session_store: memory` in health) |
| set | Postgres (`session_store: postgres`) |

On API startup (and `docker compose` api `command`), migrations run automatically via `init_store()`.

## Local

```bash
docker compose up db -d
export DATABASE_URL=postgresql://hypatia:hypatia@127.0.0.1:5432/hypatia
./scripts/apply_migrations.sh
./scripts/run_api_local.sh
```

Sessions survive API restart when using Postgres.

## Full stack

```bash
docker compose up --build
```

API container runs `python -m hypatia.db migrate` before uvicorn.
