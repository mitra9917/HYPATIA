"""Playbook #56 / issue #64 — ops mode flip latency."""

from __future__ import annotations

import os
import time

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.runtime_ops import OpsMode, set_ops_mode  # noqa: E402

get_settings.cache_clear()


def test_ops_fixture_flip_under_five_seconds() -> None:
    set_ops_mode(None)
    client = TestClient(app)
    started = time.monotonic()
    r = client.post("/api/ops/mode", json={"mode": "fixture"})
    assert r.status_code == 200
    assert time.monotonic() - started < 5.0
    h = client.get("/api/health").json()
    assert h["ops"]["ops_mode"] == "fixture"
    set_ops_mode(OpsMode.fixture)
