"""Playbook #53 / issue #35 — tool library API."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_library_tools_lists_promoted_entry() -> None:
    client = TestClient(app)
    client.post("/api/toolsmith/test-promoted")
    lib = client.get("/api/library/tools").json()
    assert lib["count"] >= 1
    assert any(t["id"] == "pendulum_angle_from_track" for t in lib["tools"])
