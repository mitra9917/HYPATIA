"""Playbook #48 / #62 — upload consent."""

from __future__ import annotations

import io
import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_upload_requires_consent() -> None:
    client = TestClient(app)
    files = {"file": ("clip.mp4", io.BytesIO(b"fake"), "video/mp4")}
    bad = client.post("/api/sessions", files=files, data={"source_type": "upload"})
    assert bad.status_code == 422

    ok = client.post(
        "/api/sessions",
        files=files,
        data={"source_type": "upload", "upload_consent": "true"},
    )
    assert ok.status_code == 200
    assert ok.json()["session"]["upload_consent"] is True
