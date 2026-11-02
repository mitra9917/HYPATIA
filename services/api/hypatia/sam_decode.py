"""Lightweight SAM response parsing — JSON fallback + meta_sam_parser (P1.11 / #51)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import FIXTURE_DIR
from .models import BBoxNorm, MaskFrame
from .sam_parser_bridge import (
    load_fixture_boxes,
    mask_frames_from_snapshot,
    parse_raw_sam_output,
    snapshot_from_fixture_boxes,
)

SAM_FIXTURE = FIXTURE_DIR / "sam" / "pendulum_boxes.json"


def _bbox_from_any(raw: dict[str, Any]) -> BBoxNorm | None:
    if "bbox_norm" in raw and isinstance(raw["bbox_norm"], dict):
        b = raw["bbox_norm"]
        return BBoxNorm(x=float(b["x"]), y=float(b["y"]), w=float(b["w"]), h=float(b["h"]))
    if all(k in raw for k in ("x", "y", "w", "h")):
        return BBoxNorm(
            x=float(raw["x"]),
            y=float(raw["y"]),
            w=float(raw["w"]),
            h=float(raw["h"]),
        )
    if all(k in raw for k in ("x1", "y1", "x2", "y2")):
        x1, y1, x2, y2 = float(raw["x1"]), float(raw["y1"]), float(raw["x2"]), float(raw["y2"])
        if max(x2, y2) <= 1.5:
            return BBoxNorm(x=x1, y=y1, w=max(x2 - x1, 0.01), h=max(y2 - y1, 0.01))
    return None


def mask_frames_from_payload(payload: Any) -> list[MaskFrame]:
    frames: list[MaskFrame] = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("frames") or payload.get("mask_frames") or payload.get("tracks") or []
        if isinstance(items, dict):
            items = items.get("frames") or []
    else:
        return frames

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        bbox = _bbox_from_any(item)
        if bbox is None and "box" in item and isinstance(item["box"], dict):
            bbox = _bbox_from_any(item["box"])
        if bbox is None:
            continue
        frames.append(
            MaskFrame(
                frame_index=int(item.get("frame_index", item.get("frame", i))),
                t_s=float(item.get("t_s", item.get("t", i / 30.0))),
                bbox_norm=bbox,
                track_id=int(item.get("track_id", item.get("id", 0))),
            )
        )
    return frames


def parse_sam_response(
    raw: str | dict[str, Any],
    *,
    width: int = 1280,
    height: int = 720,
    fps: float = 30.0,
) -> list[MaskFrame]:
    """Decode SAM output: meta_sam_parser first, then legacy JSON heuristics."""
    if isinstance(raw, dict):
        inner = raw.get("raw", raw)
        if isinstance(inner, str):
            return parse_sam_response(inner, width=width, height=height, fps=fps)
        return mask_frames_from_payload(raw)

    text = raw.strip()
    if not text:
        return []

    try:
        frames = parse_raw_sam_output(text, width=width, height=height, fps=fps)
        if frames:
            return frames
    except Exception:  # noqa: BLE001
        pass

    try:
        data = json.loads(text)
        return mask_frames_from_payload(data)
    except json.JSONDecodeError:
        pass

    for match in re.finditer(r"\{[\s\S]*\}|\[[\s\S]*\]", text):
        try:
            data = json.loads(match.group(0))
            frames = mask_frames_from_payload(data)
            if frames:
                return frames
        except json.JSONDecodeError:
            continue
    return []


def load_sam_fixture_masks(path: Path | None = None) -> list[MaskFrame]:
    """Fixture boxes → mask frames (CI / replay without Meta)."""
    fixture = path or SAM_FIXTURE
    boxes, w, h = load_fixture_boxes(str(fixture))
    snap = snapshot_from_fixture_boxes(boxes, width=w, height=h)
    return mask_frames_from_snapshot(snap, width=w, height=h, fps=30.0)
