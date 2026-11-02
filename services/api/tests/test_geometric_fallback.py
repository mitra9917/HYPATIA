"""Playbook #37 / #29 — geometric ghost when Muse Image fails."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = "live-test"

from hypatia.app import app  # noqa: E402
from hypatia.config import Settings, get_settings  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_imagine_fixture_uses_geometric_source(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    for stage in ("observe", "measure", "hypothesize", "imagine"):
        r = client.post(f"/api/sessions/{sid}/{stage}")
        assert r.status_code == 200, r.text
    frame = r.json()["session"]["imagination"][0]
    assert frame["source"] == "geometric"


def test_muse_image_failure_falls_back_to_geometric(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    for stage in ("observe", "measure", "hypothesize"):
        assert client.post(f"/api/sessions/{sid}/{stage}").status_code == 200

    settings = Settings(model_api_key="LLM_test", fixture_mode=False)
    with patch("hypatia.orchestrator.get_settings", return_value=settings):
        with patch("hypatia.pipeline.get_settings", return_value=settings):
            with patch(
                "hypatia.meta_client.MetaClient.generate_image",
                side_effect=RuntimeError("image down"),
            ):
                r = client.post(f"/api/sessions/{sid}/imagine")
    assert r.status_code == 200
    assert r.json()["session"]["imagination"][0]["source"] == "geometric"
