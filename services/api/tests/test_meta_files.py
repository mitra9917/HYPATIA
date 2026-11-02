"""P1.10 Meta Files API — one upload per session (Playbook #15 / #50)."""

from __future__ import annotations

import os

from hypatia.meta_files import (
    count_successful_file_uploads,
    ensure_session_video_file_id,
    primary_video_file_id,
    register_meta_file_id,
)
from hypatia.models import Session, SessionStatus

os.environ.setdefault("FIXTURE_MODE", "true")


def test_register_meta_file_id_dedupes() -> None:
    session = Session(id="s1")
    register_meta_file_id(session, "file-abc")
    register_meta_file_id(session, "file-abc")
    assert session.meta_file_ids == ["file-abc"]
    assert session.video_file_id == "file-abc"


def test_primary_video_file_id_prefers_video_file_id() -> None:
    session = Session(id="s2", video_file_id="v1", meta_file_ids=["v0"])
    assert primary_video_file_id(session) == "v1"


def test_ensure_skips_upload_when_file_id_present() -> None:
    class FakeRouter:
        enabled = True
        uploads = 0

        def upload_video_bytes(self, data: bytes, filename: str) -> tuple[str, dict]:
            FakeRouter.uploads += 1
            return "new-id", {"kind": "files.create", "ok": True}

    session = Session(
        id="s3",
        mode="live",
        filename="/nonexistent/path.mp4",
        meta_file_ids=["existing-id"],
        video_file_id="existing-id",
    )
    router = FakeRouter()
    result = ensure_session_video_file_id(session, router)  # type: ignore[arg-type]
    assert result == "existing-id"
    assert FakeRouter.uploads == 0


def test_count_successful_file_uploads() -> None:
    session = Session(
        id="s4",
        meta_calls=[
            {"kind": "files.create", "ok": True},
            {"kind": "files.create", "ok": False},
            {"kind": "responses", "ok": True},
        ],
    )
    assert count_successful_file_uploads(session) == 1
