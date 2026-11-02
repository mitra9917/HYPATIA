"""Meta Files API — upload-once `file_id` reuse per session (P1.10 / Playbook #15, issue #50)."""

from __future__ import annotations

from pathlib import Path

from .config import Settings, get_settings
from .model_router import ModelRouter
from .models import Session


def register_meta_file_id(session: Session, file_id: str, *, kind: str = "video") -> None:
    """Append Meta file id once; keep primary video id in sync for Observer + SAM."""
    if file_id and file_id not in session.meta_file_ids:
        session.meta_file_ids.append(file_id)
    if kind == "video" and file_id:
        session.video_file_id = file_id


def primary_video_file_id(session: Session) -> str | None:
    if session.video_file_id:
        return session.video_file_id
    return session.meta_file_ids[0] if session.meta_file_ids else None


def count_successful_file_uploads(session: Session) -> int:
    return sum(
        1
        for call in session.meta_calls
        if call.get("kind") == "files.create" and call.get("ok") is True
    )


def _read_session_video(session: Session) -> tuple[bytes, str] | None:
    if not session.filename:
        return None
    path = Path(session.filename)
    if not path.is_file():
        return None
    return path.read_bytes(), path.name


def ensure_session_video_file_id(
    session: Session,
    router: ModelRouter,
    *,
    settings: Settings | None = None,
) -> str | None:
    """
    Upload local session media to Meta Files API at most once in live mode.
    Fixture mode uses local path only (no Meta upload).
    """
    settings = settings or get_settings()
    if session.mode == "fixture" or not router.enabled:
        return None

    existing = primary_video_file_id(session)
    if existing:
        return existing

    video = _read_session_video(session)
    if not video:
        return None

    data, name = video
    file_id, log = router.upload_video_bytes(data, name)
    register_meta_file_id(session, file_id, kind="video")
    session.meta_calls.append(log)
    session.events.append(
        {
            "stage": "files",
            "message": f"Meta Files API: one upload for session ({file_id[:12]}…)",
        }
    )
    return file_id
