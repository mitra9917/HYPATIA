"""Playbooks #39–#41 / issues #30, #31 — experiment propose + result."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_experiment_propose_and_result() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    client.post(f"/api/sessions/{sid}/measure")
    client.post(f"/api/sessions/{sid}/hypothesize")

    prop = client.post(f"/api/sessions/{sid}/experiment/propose")
    assert prop.status_code == 200
    assert "Double the string length" in prop.json()["session"]["experiment"]["instruction"]

    sid2 = client.post("/api/sessions").json()["session"]["id"]
    bad = client.post(f"/api/sessions/{sid2}/experiment/result", json={"notes": "early"})
    assert bad.status_code == 422

    res = client.post(
        f"/api/sessions/{sid}/experiment/result",
        json={"notes": "Doubled length", "observed_period_ratio": 1.41, "supports_winner": True},
    )
    assert res.status_code == 200
    assert res.json()["session"]["experiment_result"]["observed_period_ratio"] == 1.41
