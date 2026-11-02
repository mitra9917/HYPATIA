"""Playbook #47 / #60 — law library + second-session hint."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402

get_settings.cache_clear()


def test_library_lists_accepted_law_and_second_session_hint() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions").json()["session"]["id"]
    for stage in ("observe", "measure", "hypothesize", "imagine", "experiment"):
        client.post(f"/api/sessions/{sid}/{stage}")
    client.post(f"/api/sessions/{sid}/accept")

    lib = client.get("/api/library/laws").json()
    assert lib["count"] >= 1
    assert lib["laws"][0]["law_latex"]

    sid2 = client.post("/api/sessions").json()["session"]
    assert sid2.get("library_hint") or any(
        e.get("stage") == "library" for e in sid2.get("events", [])
    )
