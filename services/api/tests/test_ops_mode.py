"""Playbook #45 / #33 — runtime ops mode."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.runtime_ops import OpsMode, set_ops_mode  # noqa: E402

get_settings.cache_clear()


def test_ops_mode_flip_fixture_without_redeploy() -> None:
    set_ops_mode(None)
    client = TestClient(app)
    h0 = client.get("/api/health").json()
    assert h0["ops"]["ops_mode"] == "fixture"

    r = client.post("/api/ops/mode", json={"mode": "hybrid"})
    assert r.status_code == 422  # no key in CI

    r2 = client.post("/api/ops/mode", json={"mode": "fixture"})
    assert r2.status_code == 200
    assert r2.json()["ops_mode"] == "fixture"

    set_ops_mode(OpsMode.fixture)
    h1 = client.get("/api/health").json()
    assert h1["fixture_mode"] is True
