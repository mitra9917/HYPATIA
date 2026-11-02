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


def save_imagination_frame(session_id: str, data: bytes | None, *, index: int = 0) -> str:
    path = imagination_frame_path(session_id, index)
    path.write_bytes(data if data else _TINY_PNG)
    return imagination_frame_uri(session_id, index)


def count_session_image_spend(meta_calls: list[dict]) -> float:
    return sum(float(row.get("image_spend_usd_est") or 0) for row in meta_calls if row.get("ok"))
