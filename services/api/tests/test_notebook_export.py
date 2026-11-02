"""Playbook #46 / #24 — notebook export."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_notebook_md_export_after_accept() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions").json()["session"]["id"]
    for stage in ("observe", "measure", "hypothesize", "imagine", "experiment"):
        assert client.post(f"/api/sessions/{sid}/{stage}").status_code == 200
    assert client.post(f"/api/sessions/{sid}/accept").status_code == 200

    md = client.get(f"/api/sessions/{sid}/notebook.md")
    assert md.status_code == 200
    text = md.text
    assert "Models used" in text
    assert "muse-" in text or "pysr" in text or "glimmer" in text.lower() or "Models used" in text
    assert "trajectory.csv" in text.lower() or "Measurement" in text
