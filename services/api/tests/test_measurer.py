"""P1.4 SAM measurer tests (Playbook #18 / #13)."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.app import app  # noqa: E402
from hypatia.config import get_settings  # noqa: E402
from hypatia.measurer import (  # noqa: E402
    estimate_frame_cost,
    load_cached_track,
    run_measurer,
    save_cached_track,
    trajectory_to_mask_frames,
)
from hypatia.meta_client import MetaClient  # noqa: E402
from hypatia.models import Session, SessionStatus, Track  # noqa: E402
from hypatia.observer import run_observer  # noqa: E402
from hypatia.sam_decode import parse_sam_response  # noqa: E402
from hypatia.science import synthesize_pendulum_track  # noqa: E402
from hypatia.store import store  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_frame_cost_in_scientific_fps_band() -> None:
    fc = estimate_frame_cost(clip_duration_s=4.0, source_fps=30.0, scientific_fps=12.5)
    assert 40 <= fc.frames_billed_estimate <= 60
    assert fc.scientific_fps == 12.5


def test_parse_sam_json_masks() -> None:
    raw = json.dumps(
        {
            "frames": [
                {"frame_index": 0, "t_s": 0.0, "bbox_norm": {"x": 0.4, "y": 0.3, "w": 0.1, "h": 0.1}},
                {"frame_index": 1, "t_s": 0.08, "x": 0.41, "y": 0.31, "w": 0.1, "h": 0.1},
            ]
        }
    )
    frames = parse_sam_response(raw)
    assert len(frames) == 2
    assert frames[0].bbox_norm.w == pytest.approx(0.1)


def test_trajectory_to_mask_frames_non_empty() -> None:
    pts = synthesize_pendulum_track(duration_s=1.0, fps=10.0)
    masks = trajectory_to_mask_frames(pts, length_m=0.45)
    assert len(masks) >= 2


def test_default_fixture_track_loads() -> None:
    track = load_cached_track("no-session", "pendulum bob")
    assert track is not None
    assert track.sam_prompt
    assert len(track.points) >= 10


def test_run_measurer_fixture_populates_masks_and_cost() -> None:
    session = Session(id="meas-test-1", status=SessionStatus.observing, mode="fixture")
    store.put(session)
    asyncio.run(run_observer(session))
    settings = get_settings()
    client = MetaClient(settings, session_id=session.id)
    out = asyncio.run(run_measurer(session, client, settings))
    assert out.tracks
    t = out.tracks[0]
    assert len(t.points) >= 10
    assert len(t.mask_frames) >= 2
    assert t.frame_cost is not None
    kinds = [c.get("kind") for c in out.meta_calls]
    assert "measurer.frame_cost" in kinds


def test_measure_after_observe_endpoint(client: TestClient) -> None:
    sid = client.post("/api/sessions").json()["session"]["id"]
    client.post(f"/api/sessions/{sid}/observe")
    resp = client.post(f"/api/sessions/{sid}/measure")
    assert resp.status_code == 200
    body = resp.json()["session"]
    assert body["status"] == "measuring"
    assert body["tracks"][0]["mask_frames"]
    assert body["tracks"][0]["source"] in {"fixture", "sam", "hybrid"}


def test_cache_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hypatia.measurer.TRACK_FIXTURE_DIR", tmp_path)
    track = Track(object_name="bob", sam_prompt="pendulum bob", points=synthesize_pendulum_track(duration_s=0.5))
    save_cached_track("sess-abc", "pendulum bob", track)
    loaded = load_cached_track("sess-abc", "pendulum bob")
    assert loaded is not None
    assert loaded.sam_prompt == "pendulum bob"
