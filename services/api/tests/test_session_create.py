"""Session create API — webcam source_type (P1.13 / #53)."""

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


def test_post_session_fixture_without_file(client: TestClient) -> None:
    r = client.post("/api/sessions")
    assert r.status_code == 200
    assert r.json()["session"]["source_type"] == "fixture"


def test_post_session_upload_source(client: TestClient) -> None:
    files = {"file": ("clip.mp4", b"\x00\x00", "video/mp4")}
    r = client.post("/api/sessions", files=files)
    assert r.status_code == 200
    assert r.json()["session"]["source_type"] == "upload"


def test_post_session_webcam_source(client: TestClient) -> None:
    files = {"file": ("burst.webm", b"webm", "video/webm")}
    data = {"source_type": "webcam"}
    r = client.post("/api/sessions", files=files, data=data)
    assert r.status_code == 200
    assert r.json()["session"]["source_type"] == "webcam"
