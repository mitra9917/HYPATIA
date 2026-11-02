"""SAM 3.1 decode via meta_sam_parser (P1.11 / Playbook #19, issue #51)."""

from __future__ import annotations

import json
import re
from typing import Any

from meta_sam_parser import (
    CompletedOutcome,
    FrameReference,
    SegmentationBoxRecord,
    VideoSegmentationSnapshot,
    video_segmentation_format,
)

from .models import BBoxNorm, MaskFrame


def object_id_to_track_id(object_id: str) -> int:
    """Stable small int track id from SAM object id string."""
    if object_id.isdigit():
        return int(object_id)
    digits = re.sub(r"\D", "", object_id)
    if digits:
        return int(digits) % 10_000
    return abs(hash(object_id)) % 10_000


def mask_frames_from_snapshot(
    snapshot: VideoSegmentationSnapshot,
    *,
    width: int,
    height: int,
    fps: float = 30.0,
) -> list[MaskFrame]:
    """Convert parser snapshot records → normalized overlay frames (server-side JSON)."""
    if width <= 0 or height <= 0:
        return []
    frames: list[MaskFrame] = []
    for record in snapshot.records:
        if not isinstance(record, SegmentationBoxRecord):
            continue
        frame_index = record.frame.frame_index if record.frame else 0
        t_s = frame_index / fps
        x = record.left / width
        y = record.top / height
        w = max((record.right - record.left) / width, 0.01)
        h = max((record.bottom - record.top) / height, 0.01)
        frames.append(
            MaskFrame(
                frame_index=frame_index,
                t_s=t_s,
                bbox_norm=BBoxNorm(
                    x=min(max(x, 0.0), 1.0 - w),
                    y=min(max(y, 0.0), 1.0 - h),
                    w=min(w, 1.0),
                    h=min(h, 1.0),
                ),
                track_id=object_id_to_track_id(record.object_id),
            )
        )
    frames.sort(key=lambda f: (f.frame_index, f.track_id))
    return frames


def parse_raw_sam_output(
    text: str,
    *,
    width: int,
    height: int,
    fps: float = 30.0,
) -> list[MaskFrame]:
    """Parse SAM API output text with meta_sam_parser video format."""
    stripped = text.strip()
    if not stripped:
        return []
    fmt = video_segmentation_format()
    parser = fmt.create_parser()
    parser.push(stripped, emit=False)
    finish = parser.finish(CompletedOutcome())
    result = finish.result
    if not isinstance(result, VideoSegmentationSnapshot):
        return []
    return mask_frames_from_snapshot(result, width=width, height=height, fps=fps)


def snapshot_from_fixture_boxes(
    boxes: list[dict[str, Any]],
    *,
    width: int,
    height: int,
) -> VideoSegmentationSnapshot:
    """Build snapshot from JSON fixture rows for tests."""
    records: list[SegmentationBoxRecord] = []
    for i, row in enumerate(boxes):
        frame_idx = int(row.get("frame_index", 0))
        records.append(
            SegmentationBoxRecord(
                order=i,
                object_id=str(row.get("object_id", "1")),
                left=float(row["left"]),
                top=float(row["top"]),
                right=float(row["right"]),
                bottom=float(row["bottom"]),
                frame=FrameReference(frame_index=frame_idx),
            )
        )
    return VideoSegmentationSnapshot(revision=1, records=tuple(records), diagnostics=(), raw_output="")


def load_fixture_boxes(path: str) -> tuple[list[dict[str, Any]], int, int]:
    from pathlib import Path as _Path

    data = json.loads(_Path(path).read_text(encoding="utf-8"))
    media = data.get("media", {})
    w = int(media.get("width", 1280))
    h = int(media.get("height", 720))
    return list(data.get("boxes", [])), w, h
