"""Session API + SSE progress (P1.6 / Playbook #22, issue #15)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.session_events import publish, reset_subscribers_for_tests, subscribe  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    reset_subscribers_for_tests()
    return TestClient(app)


def test_events_404_unknown_session(client: TestClient) -> None:
    r = client.get("/api/sessions/does-not-exist/events")
    assert r.status_code == 404


def test_events_snapshot_on_connect(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    with client.stream("GET", f"/api/sessions/{sid}/events") as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        chunk = next(resp.iter_text())
        assert "event: snapshot" in chunk
        assert sid in chunk
        assert "created" in chunk or "status" in chunk


def test_observe_measure_emit_stage_events(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    body = client.get(f"/api/sessions/{sid}").json()
    events = body.get("events") or []
    names = [e.get("event") for e in events if isinstance(e, dict)]
    assert "stage_started" in names
    assert "stage_completed" in names
    assert any(e.get("stage") == "observe" for e in events)

    client.post(f"/api/sessions/{sid}/measure")
    body2 = client.get(f"/api/sessions/{sid}").json()
    measure_events = [e for e in body2.get("events", []) if e.get("stage") == "measure"]
    assert measure_events
    assert any(e.get("event") == "stage_completed" for e in measure_events)


def test_publish_reaches_sse_queue() -> None:
    reset_subscribers_for_tests()
    q = subscribe("sse-unit")
    publish("sse-unit", "ping", {"ok": True})

    async def read_one():
        return await q.get()

    import asyncio

    msg = asyncio.run(read_one())
    assert msg["event"] == "ping"
    assert msg["data"]["ok"] is True

