"""Read uploaded session media dimensions for SAM decode normalization."""

from __future__ import annotations

from pathlib import Path

from .models import Session


def session_media_size(session: Session, *, default: tuple[int, int] = (1280, 720)) -> tuple[int, int]:
    path = session.filename
    if not path:
        return default
    p = Path(path)
    if not p.is_file():
        return default
    try:
        import cv2

        cap = cv2.VideoCapture(str(p))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or default[0]
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or default[1]
        cap.release()
        if w > 0 and h > 0:
            return w, h
    except Exception:  # noqa: BLE001
        pass
    return default
