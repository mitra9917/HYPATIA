"""Lightweight SAM response parsing until P1.11 (#51) wires meta_sam_parser."""

from __future__ import annotations

import json
import re
from typing import Any

from .models import BBoxNorm, MaskFrame


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
    # xyxy pixel-ish → rough norm if values look like 0–1 already
    if all(k in raw for k in ("x1", "y1", "x2", "y2")):
        x1, y1, x2, y2 = float(raw["x1"]), float(raw["y1"]), float(raw["x2"]), float(raw["y2"])
        if max(x2, y2) <= 1.5:
            return BBoxNorm(x=x1, y=y1, w=max(x2 - x1, 0.01), h=max(y2 - y1, 0.01))
    return None


def mask_frames_from_payload(payload: Any) -> list[MaskFrame]:
    """Extract mask frames from parsed JSON (flexible shapes)."""
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


def parse_sam_response(raw: str | dict[str, Any]) -> list[MaskFrame]:
    """Best-effort decode of SAM 3.1 text/JSON (full parser in #51)."""
    if isinstance(raw, dict):
        inner = raw.get("raw", raw)
        if isinstance(inner, str):
            return parse_sam_response(inner)
        return mask_frames_from_payload(raw)

    text = raw.strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        return mask_frames_from_payload(data)
    except json.JSONDecodeError:
        pass

    # JSON blob embedded in prose
    for match in re.finditer(r"\{[\s\S]*\}|\[[\s\S]*\]", text):
        try:
            data = json.loads(match.group(0))
            frames = mask_frames_from_payload(data)
            if frames:
                return frames
        except json.JSONDecodeError:
            continue
    return []
