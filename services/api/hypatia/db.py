"""Postgres migrations + connection (P1.15 / Playbook #21, issue #55)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import psycopg

from .config import get_settings

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def connect(database_url: str) -> psycopg.Connection:
    return psycopg.connect(database_url)


def run_migrations(database_url: str) -> list[str]:
    """Apply pending SQL migrations; returns versions applied this run."""
    applied_now: list[str] = []
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    with connect(database_url) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            conn.commit()
            for path in files:
                version = path.stem
                cur.execute("SELECT 1 FROM schema_migrations WHERE version = %s", (version,))
                if cur.fetchone():
                    continue
                sql = path.read_text(encoding="utf-8")
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    (version,),
                )
                conn.commit()
                applied_now.append(version)
                logger.info("Applied migration %s", version)
    return applied_now


def main() -> None:
    """CLI: python -m hypatia.db migrate"""
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        settings = get_settings()
        url = settings.database_url.strip()
        if not url:
            print("DATABASE_URL not set; nothing to migrate", file=sys.stderr)
            sys.exit(1)
        applied = run_migrations(url)
        print("Applied:", applied or "(none — already up to date)")
        return
    print("Usage: python -m hypatia.db migrate", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
