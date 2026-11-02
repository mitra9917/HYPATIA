"""P1.3 Observer fixture and schema tests."""

from __future__ import annotations

import asyncio
import os

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.models import Session, SessionStatus  # noqa: E402
from hypatia.observer import load_pendulum_fixture, run_observer  # noqa: E402
from hypatia.store import store  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_pendulum_fixture_has_sam_prompts() -> None:
    brief = load_pendulum_fixture()
    assert len(brief.sam_prompts) >= 1
    assert any("pendulum" in p.lower() or "bob" in p.lower() for p in brief.sam_prompts)
    assert brief.suggested_domain == "mechanics.pendulum"
    assert brief.narration.strip()
    assert "fallback" not in brief.narration.lower()


def test_run_observer_fixture_mode() -> None:
    session = Session(id="test-obs", status=SessionStatus.created, mode="fixture")
    store.put(session)
    out = asyncio.run(run_observer(session))
    assert out.scene is not None
    assert len(out.scene.sam_prompts) >= 2
    assert out.meta_calls[-1]["kind"] == "observer"


def test_observe_endpoint(client: TestClient) -> None:
    created = client.post("/api/sessions").json()["session"]
    sid = created["id"]
    resp = client.post(f"/api/sessions/{sid}/observe")
    assert resp.status_code == 200
    body = resp.json()["session"]
    assert body["scene"]["sam_prompts"]
    assert body["scene"]["narration"].strip()
    assert body["status"] == "observing"
