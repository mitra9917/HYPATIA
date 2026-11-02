"""Playbook #55 / issue #37 — VERITAS fixture verdict."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_veritas_fake_physics_verdict() -> None:
    client = TestClient(app)
    r = client.post("/api/veritas/analyze")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["verdict"] == "not_physical"
    assert body["break_frame"] == 41
    assert "9.8" in body["headline"] or "g" in body["headline"].lower()
