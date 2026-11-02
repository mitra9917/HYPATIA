"""P1.16 orchestrator contract tests (Playbook #16 / #56)."""

from __future__ import annotations

import os
from unittest.mock import patch

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


def test_happy_path_stage_by_stage(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    for stage in ("observe", "measure", "hypothesize", "imagine", "experiment", "accept"):
        r = client.post(f"/api/sessions/{sid}/{stage}")
        assert r.status_code == 200, (stage, r.text)
    body = r.json()["session"]
    assert body["status"] == "accepted"
    assert body["notebook"] is not None


def test_observe_records_pi_plan(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    r = client.post(f"/api/sessions/{sid}/observe")
    assert r.status_code == 200
    assert "observe" in r.json()["session"]["pi_plans"]


def test_hypothesize_before_measure_returns_422(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    r = client.post(f"/api/sessions/{sid}/hypothesize")
    assert r.status_code == 422
    assert "measure" in r.json()["detail"].lower()


def test_hypothesize_returns_ranked_rivals(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    client.post(f"/api/sessions/{sid}/measure")
    r = client.post(f"/api/sessions/{sid}/hypothesize")
    assert r.status_code == 200
    hyps = r.json()["session"]["hypotheses"]
    assert len(hyps) >= 3
    assert hyps[0]["status"] == "winner"
    scores = [h["heldout_score"] for h in hyps]
    assert scores == sorted(scores, reverse=True)
    assert "hypothesize" in r.json()["session"]["pi_plans"]


def test_fail_at_measure_then_resume(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")

    with patch("hypatia.orchestrator._measure", side_effect=RuntimeError("test measure failure")):
        r = client.post(f"/api/sessions/{sid}/measure")
        assert r.status_code == 200
        assert r.json()["session"]["status"] == "failed"

    failed = client.get(f"/api/sessions/{sid}").json()
    assert failed["status"] == "failed"
    assert "test measure failure" in (failed.get("error") or "")

    r2 = client.post(f"/api/sessions/{sid}/measure")
    assert r2.status_code == 200
    assert r2.json()["session"]["tracks"]

    r3 = client.post(f"/api/sessions/{sid}/run", params={"from_stage": "hypothesize"})
    assert r3.status_code == 200
    assert r3.json()["session"]["status"] == "accepted"
