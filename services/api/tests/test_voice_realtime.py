"""Playbook #49 / #61 — voice WebSocket."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_voice_realtime_websocket_commit() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/voice/realtime") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "ready"
        assert "fallback" in ready
        ws.send_json({"type": "commit", "transcript": "Double the length?"})
        final = ws.receive_json()
        assert final["type"] == "final"
        reply = ws.receive_json()
        assert reply["type"] == "reply"
