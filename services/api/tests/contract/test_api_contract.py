"""P2.9 contract tests — fixture payloads, no MODEL_API_KEY (Playbook #38 / #58)."""

from __future__ import annotations

import json
import os

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.agent_schemas import exported_schemas  # noqa: E402
from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.models import SceneBrief, Session  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_exported_agent_schemas_have_titles() -> None:
    schemas = exported_schemas()
    assert "SceneBrief" in schemas
    assert schemas["SceneBrief"]["type"] == "object"
    assert "HypothesisBatch" in schemas
    assert "NextTest" in schemas


def test_scene_brief_roundtrip_fixture() -> None:
    root = Path(__file__).resolve().parents[4]
    raw = json.loads((root / "data" / "fixtures" / "observer_pendulum.json").read_text())
    brief = SceneBrief.model_validate(raw)
    assert brief.sam_prompts


def test_observe_response_matches_session_model(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    resp = client.post(f"/api/sessions/{sid}/observe")
    assert resp.status_code == 200
    Session.model_validate(resp.json()["session"])


def test_hypothesize_response_has_train_and_heldout(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    client.post(f"/api/sessions/{sid}/measure")
    resp = client.post(f"/api/sessions/{sid}/hypothesize")
    body = resp.json()["session"]
    Session.model_validate(body)
    winner = next(h for h in body["hypotheses"] if h["status"] == "winner")
    assert "train_score" in winner and "heldout_score" in winner
    assert winner["param_ci"].get("g")
