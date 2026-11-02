"""Playbook #52 / issue #34 — Toolsmith promoted tool test on fixture frames."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_toolsmith_promoted_tool_passes_on_fixture_track(client: TestClient) -> None:
    r = client.post("/api/toolsmith/test-promoted")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["returncode"] == 0
    assert "mean_angle" in body["stdout"]
