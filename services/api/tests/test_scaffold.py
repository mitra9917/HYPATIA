"""P1.1 scaffold checks — no Meta key required."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()

from hypatia.app import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_hypatia_package_imports() -> None:
    import hypatia.config  # noqa: F401
    import hypatia.meta_client  # noqa: F401
    import hypatia.pipeline  # noqa: F401


def test_health_ok_and_fixture_mode(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["fixture_mode"] is True
    assert body["service"] == "hypatia-api"


def test_health_exposes_model_router(client: TestClient) -> None:
    router = client.get("/api/health").json()["model_router"]
    assert router["observer"] == "muse-spark-1.3"
    assert router["sam"] == "sam-3.1"
    assert router["pi"] == "muse-wonder-1.0"
    assert "base_url" in router
