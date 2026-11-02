"""Fixture recorder tests (Playbook #23 / issue #18)."""

from __future__ import annotations

import json
from pathlib import Path

from hypatia.fixture_recorder import (
    masks_to_sam_boxes,
    write_observer_fixture,
    write_track_fixture,
)
from hypatia.models import BBoxNorm, MaskFrame, SceneBrief, SceneObject, Track, TrajectoryPoint


def test_write_observer_fixture(tmp_path: Path) -> None:
    scene = SceneBrief(
        objects=[SceneObject(name="bob", why_interesting="swing")],
        candidate_variables=["angle"],
        sam_prompts=["pendulum bob"],
        suggested_domain="mechanics.pendulum",
        narration="test",
    )
    path = write_observer_fixture(scene, tmp_path / "obs.json")
    data = json.loads(path.read_text())
    assert data["suggested_domain"] == "mechanics.pendulum"


def test_masks_to_sam_boxes() -> None:
    masks = [
        MaskFrame(frame_index=0, t_s=0.0, bbox_norm=BBoxNorm(x=0.5, y=0.4, w=0.05, h=0.05), track_id=1),
    ]
    payload = masks_to_sam_boxes(masks, width=1000, height=500)
    assert payload["media"]["width"] == 1000
    assert payload["boxes"][0]["left"] == 500


def test_write_track_fixture(tmp_path: Path) -> None:
    track = Track(
        object_name="bob",
        sam_prompt="pendulum bob",
        points=[TrajectoryPoint(t=0.0, angle_rad=0.1, length_m=0.4)],
        source="sam",
    )
    path = write_track_fixture(track, tmp_path / "t.json")
    assert Track.model_validate_json(path.read_text()).sam_prompt == "pendulum bob"
