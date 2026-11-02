"""Capture live Observer + SAM outputs into repo fixtures (P1.9 / Playbook #23, issue #18)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import FIXTURE_DIR
from .models import MaskFrame, SceneBrief, Session, Track

OBSERVER_CANONICAL = FIXTURE_DIR / "observer_pendulum.json"
SAM_CANONICAL = FIXTURE_DIR / "sam" / "pendulum_boxes.json"
TRACK_FIXTURE_DIR = FIXTURE_DIR / "tracks"


def _slug(prompt: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "_", prompt.lower().strip()).strip("_") or "object"


def default_track_fixture_path(prompt: str) -> Path:
    slug = _slug(prompt)
    if "bob" in slug or slug == "pendulum_bob":
        return TRACK_FIXTURE_DIR / "pendulum_bob_default.json"
    return TRACK_FIXTURE_DIR / f"{slug}_default.json"


def write_observer_fixture(scene: SceneBrief, path: Path | None = None) -> Path:
    dest = path or OBSERVER_CANONICAL
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(scene.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return dest


def write_track_fixture(track: Track, path: Path | None = None, *, prompt: str | None = None) -> Path:
    dest = path or default_track_fixture_path(prompt or track.sam_prompt)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(track.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return dest


def masks_to_sam_boxes(
    masks: list[MaskFrame],
    *,
    width: int = 1280,
    height: int = 720,
    fps: float = 30.0,
) -> dict[str, Any]:
    """Convert decoded mask frames to `data/fixtures/sam/*.json` box records."""
    boxes: list[dict[str, Any]] = []
    for m in masks:
        bb = m.bbox_norm
        left = int(round(bb.x * width))
        top = int(round(bb.y * height))
        right = int(round((bb.x + bb.w) * width))
        bottom = int(round((bb.y + bb.h) * height))
        boxes.append(
            {
                "object_id": str(m.track_id or 1),
                "frame_index": m.frame_index,
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
            }
        )
    return {"media": {"width": width, "height": height, "fps": fps}, "boxes": boxes}


def write_sam_fixture(
    masks: list[MaskFrame],
    path: Path | None = None,
    *,
    width: int = 1280,
    height: int = 720,
    fps: float = 30.0,
) -> Path:
    dest = path or SAM_CANONICAL
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = masks_to_sam_boxes(masks, width=width, height=height, fps=fps)
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return dest


def record_session_slice(
    session: Session,
    *,
    width: int = 1280,
    height: int = 720,
    fps: float = 30.0,
    promote_canonical: bool = True,
) -> dict[str, str]:
    """
    Persist Observer scene + primary SAM track (+ optional SAM box slice) under ``data/fixtures/``.

    Returns map of logical name → file path (string).
    """
    written: dict[str, str] = {}
    if session.scene:
        dest = OBSERVER_CANONICAL if promote_canonical else FIXTURE_DIR / f"observer_{session.id[:8]}.json"
        written["observer"] = str(write_observer_fixture(session.scene, dest))

    if not session.tracks:
        return written

    track = session.tracks[0]
    prompt = track.sam_prompt or "pendulum bob"
    tdest = (
        default_track_fixture_path(prompt)
        if promote_canonical
        else TRACK_FIXTURE_DIR / f"{session.id[:8]}_{_slug(prompt)}.json"
    )
    written["track"] = str(write_track_fixture(track, tdest, prompt=prompt))

    if track.mask_frames and track.source in {"sam", "hybrid"}:
        sdest = SAM_CANONICAL if promote_canonical else FIXTURE_DIR / "sam" / f"{session.id[:8]}_boxes.json"
        written["sam"] = str(
            write_sam_fixture(track.mask_frames, sdest, width=width, height=height, fps=fps or track.fps or 30.0)
        )

    return written
