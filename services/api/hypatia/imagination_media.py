"""Persist ghost frame PNGs for imagine API (P3.2)."""

from __future__ import annotations

from pathlib import Path

from .config import MEDIA_DIR

# 1×1 PNG (valid file for fixture / geometric fallback)
_TINY_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c6300010000050001cd0a2a9b0000000049454e44ae426082"
)


def imagination_frame_path(session_id: str, index: int = 0) -> Path:
    return MEDIA_DIR / f"{session_id}_ghost_{index}.png"


def imagination_frame_uri(session_id: str, index: int = 0) -> str:
    return f"/api/sessions/{session_id}/imagination/{index}/frame.png"


def render_geometric_frame(real_xy: list[tuple[float, float]], ghost_xy: list[tuple[float, float]]) -> bytes:
    """Draw measured (blue) vs predicted ghost (orange) trajectory as a real PNG."""
    import cv2
    import numpy as np

    w, h = 640, 360
    img = np.full((h, w, 3), 250, dtype=np.uint8)
    allp = real_xy + ghost_xy
    if not allp:
        return _TINY_PNG
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    s = 0.8 * min(w, h) / span
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2

    def px(p: tuple[float, float]) -> tuple[int, int]:
        return int(w / 2 + (p[0] - cx) * s), int(h / 2 - (p[1] - cy) * s)

    for pts, color in ((real_xy, (200, 120, 30)), (ghost_xy, (40, 140, 240))):
        poly = np.array([px(p) for p in pts], dtype=np.int32)
        if len(poly) > 1:
            cv2.polylines(img, [poly], False, color, 2, cv2.LINE_AA)
        if len(poly):
            cv2.circle(img, tuple(int(v) for v in poly[-1]), 9, color, -1, cv2.LINE_AA)
    cv2.putText(img, "measured", (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 120, 30), 2, cv2.LINE_AA)
    cv2.putText(img, "predicted (ghost)", (12, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 140, 240), 2, cv2.LINE_AA)
    ok, buf = cv2.imencode(".png", img)
    return buf.tobytes() if ok else _TINY_PNG


def save_imagination_frame(session_id: str, data: bytes | None, *, index: int = 0) -> str:
    path = imagination_frame_path(session_id, index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if data else _TINY_PNG)
    return imagination_frame_uri(session_id, index)


def count_session_image_spend(meta_calls: list[dict]) -> float:
    return sum(float(row.get("image_spend_usd_est") or 0) for row in meta_calls if row.get("ok"))
