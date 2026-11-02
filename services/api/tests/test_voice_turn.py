"""Playbook #43 / issue #32 — voice turn."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_voice_turn_fixture_transcript() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    client.post(f"/api/sessions/{sid}/measure")
    client.post(f"/api/sessions/{sid}/hypothesize")
    client.post(f"/api/sessions/{sid}/experiment/propose")

    r = client.post(
        "/api/voice/turn",
        json={"session_id": sid, "transcript": "Should we double the string?"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["transcript"]
    assert body["reply"]
    assert body["fixture_mode"] is True
