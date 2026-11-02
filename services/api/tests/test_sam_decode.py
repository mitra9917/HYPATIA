"""P1.11 meta_sam_parser decode tests (Playbook #19 / #51)."""

from __future__ import annotations

import os

import pytest

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.sam_decode import load_sam_fixture_masks, parse_sam_response  # noqa: E402
from hypatia.sam_parser_bridge import (  # noqa: E402
    mask_frames_from_snapshot,
    object_id_to_track_id,
    snapshot_from_fixture_boxes,
)


def test_object_id_to_track_id_stable() -> None:
    assert object_id_to_track_id("1") == 1
    assert object_id_to_track_id("bob-42") == 42


def test_fixture_boxes_decode_to_normalized_masks() -> None:
    frames = load_sam_fixture_masks()
    assert len(frames) == 3
    assert all(0 <= f.bbox_norm.x <= 1 for f in frames)
    assert all(f.track_id == 1 for f in frames)
    assert frames[0].frame_index == 0
    assert frames[-1].frame_index == 6


def test_snapshot_from_fixture_matches_loader() -> None:
    boxes = [
        {"object_id": "2", "frame_index": 1, "left": 100, "top": 100, "right": 200, "bottom": 200}
    ]
    snap = snapshot_from_fixture_boxes(boxes, width=640, height=480)
    frames = mask_frames_from_snapshot(snap, width=640, height=480, fps=30.0)
    assert len(frames) == 1
    assert frames[0].track_id == 2
    assert frames[0].bbox_norm.w == pytest.approx(100 / 640, rel=1e-3)


def test_parse_sam_response_legacy_json_still_works() -> None:
    raw = '{"frames": [{"frame_index": 0, "t_s": 0.0, "bbox_norm": {"x": 0.1, "y": 0.2, "w": 0.05, "h": 0.05}}]}'
    frames = parse_sam_response(raw)
    assert len(frames) == 1
