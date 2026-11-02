"""Playbook #42 / #57 — accept gates."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_accept_requires_experiment_and_gates() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions").json()["session"]["id"]
    for stage in ("observe", "measure", "hypothesize", "imagine"):
        assert client.post(f"/api/sessions/{sid}/{stage}").status_code == 200

    early = client.post(f"/api/sessions/{sid}/accept")
    assert early.status_code == 422

    client.post(f"/api/sessions/{sid}/experiment/propose")
    acc = client.post(f"/api/sessions/{sid}/accept")
    assert acc.status_code == 200
    body = acc.json()["session"]
    assert body["status"] == "accepted"
    assert body["notebook"]["law_latex"]
    assert body["law_gate"]["ok"] is True
