"""Playbook #54 / issue #36 — cell domain + logistic notebook export."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_cells_observer_and_logistic_notebook() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions?domain_hint=biology.cells").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    md = client.get(f"/api/sessions/{sid}/cells-notebook.md")
    assert md.status_code == 200
    text = md.text
    assert "logistic" in text.lower() or "N(t)" in text
    assert "biology.cells" in text
