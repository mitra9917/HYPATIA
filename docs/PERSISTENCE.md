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

## Supabase (new account / production)

Direct host `db.<ref>.supabase.co` is often **IPv6-only**. If local API fails with `failed to resolve host` or DNS errors, use the **Session pooler** string from the Supabase dashboard (port **5432**, user `postgres.<ref>`), with `?sslmode=require`.

```bash
# After updating DATABASE_URL in .env
export PYTHONPATH=services/api
python3 -m hypatia.db migrate
./scripts/run_api_local.sh
curl -s http://127.0.0.1:8000/api/health | jq .session_store   # expect "postgres"
```

Cursor’s Supabase MCP plugin may still be signed into an **older** org; reconnect it to the HYPATIA project if you want dashboard actions from the agent.

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
