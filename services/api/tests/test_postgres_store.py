"""Postgres store tests (Playbook #21 / #55)."""

from __future__ import annotations

import os

import pytest

from hypatia.models import Session, SessionStatus


def test_session_document_roundtrip_json() -> None:
    session = Session(id="pg-test-1", status=SessionStatus.created, mode="fixture")
    data = session.model_dump(mode="json")
    back = Session.model_validate(data)
    assert back.id == session.id


@pytest.mark.skipif(not os.environ.get("DATABASE_URL", "").strip(), reason="DATABASE_URL not set")
def test_postgres_store_survives_reload() -> None:
    url = os.environ["DATABASE_URL"].strip()
    from hypatia.db import run_migrations
    from hypatia.postgres_store import PostgresSessionStore

    run_migrations(url)
    store = PostgresSessionStore(url)
    session = Session(id="persist-test-1", status=SessionStatus.measuring, mode="live")
    store.put(session)
    loaded = store.get("persist-test-1")
    assert loaded is not None
    assert loaded.status == SessionStatus.measuring
