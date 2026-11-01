from __future__ import annotations

import threading
from typing import Dict

from .models import Session


class InMemoryStore:
    """Hackathon-speed session store. Swap for Postgres/RDS without changing routes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, Session] = {}

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


store = InMemoryStore()
