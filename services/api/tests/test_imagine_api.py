"""Playbook #31–33 imagine API (issues #27–#28)."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.imagination_audit import metre_xy_to_bbox_norm
from hypatia.models import Hypothesis, MaskFrame, Track
from hypatia.science import G, synthesize_pendulum_track
from hypatia.store import store

get_settings.cache_clear()


def _seed_track(session_id: str) -> None:
    session = store.get(session_id)
    assert session is not None
    points = synthesize_pendulum_track(length_m=0.45, g=G, noise=0.0)
    masks = [
        MaskFrame(
            frame_index=i,
            t_s=p.t,
            bbox_norm=metre_xy_to_bbox_norm(p.x_m or 0, p.y_m or 0, length_m=0.45),
        )
        for i, p in enumerate(points[::4])
    ]
    session.tracks = [
        Track(object_name="bob", sam_prompt="round pendulum bob weight", points=points, mask_frames=masks)
    ]
    session.hypotheses = [
        Hypothesis(
            id="win",
            form_latex=r"T = 2\pi\sqrt{L/g}",
            form_plain="pendulum",
            params={"g": G, "L": 0.45},
            heldout_score=0.95,
            status="winner",
        ),
        Hypothesis(
            id="lose",
            form_latex="T=kL",
            form_plain="linear",
            params={"k": 1.0},
            heldout_score=0.2,
            status="eliminated",
        ),
    ]
    store.put(session)


def test_imagine_returns_ghost_frame_uri() -> None:
    client = TestClient(app)
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    _seed_track(sid)
    r = client.post(f"/api/sessions/{sid}/imagine")
    assert r.status_code == 200, r.text
    frame = r.json()["session"]["imagination"][0]
    assert frame.get("ghost_frame_uri")
    assert frame.get("audit_iou") is not None
    assert frame.get("mask_hint_bbox")
    img = client.get(frame["ghost_frame_uri"])
    assert img.status_code == 200
    assert img.headers["content-type"].startswith("image/")
