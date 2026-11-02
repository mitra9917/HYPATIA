from __future__ import annotations

import threading
from typing import Protocol

from .config import Settings, get_settings
from .models import Session


class SessionStore(Protocol):
    def put(self, session: Session) -> Session: ...
    def get(self, session_id: str) -> Session | None: ...
    def list_ids(self) -> list[str]: ...


class InMemoryStore:
    """Hackathon-speed session store when DATABASE_URL is unset."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, Session] = {}

    def put(self, session: Session) -> Session:
        with self._lock:
            self._sessions[session.id] = session
            return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            return self._sessions.get(session_id)

    def list_ids(self) -> list[str]:
        with self._lock:
            return list(self._sessions.keys())


_store: SessionStore = InMemoryStore()
_store_kind: str = "memory"


def init_store(settings: Settings | None = None) -> str:
    """Bind Postgres store when DATABASE_URL is set; run migrations first."""
    global _store, _store_kind
    settings = settings or get_settings()
    url = settings.database_url.strip()
    if not url:
        _store = InMemoryStore()
        _store_kind = "memory"
        return _store_kind

    from .db import run_migrations
    from .postgres_store import PostgresSessionStore

    try:
        run_migrations(url)
        _store = PostgresSessionStore(url)
        _store_kind = "postgres"
    except Exception as exc:  # noqa: BLE001
        # Demo reliability: bad DNS / Docker down / Supabase asleep → in-memory (AGENTS.md)
        import logging

        logging.getLogger(__name__).warning(
            "DATABASE_URL set but Postgres unavailable (%s); using in-memory store",
            exc,
        )
        _store = InMemoryStore()
        _store_kind = "memory_fallback"
    return _store_kind


def store_kind() -> str:
    return _store_kind


class _StoreProxy:
    def put(self, session: Session) -> Session:
        return _store.put(session)

    def get(self, session_id: str) -> Session | None:
        return _store.get(session_id)

    def list_ids(self) -> list[str]:
        return _store.list_ids()


store = _StoreProxy()
