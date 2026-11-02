"""Observer agent — Muse Spark → SceneBrief (P1.3 / Playbook #15)."""

from __future__ import annotations

import json
from pathlib import Path

from .config import FIXTURE_DIR, Settings, get_settings
from .model_router import ModelRouter
from .models import SceneBrief, SceneObject, Session, SessionStatus
from .store import store

OBSERVER_FIXTURE_PENDULUM = FIXTURE_DIR / "observer_pendulum.json"

SCENE_BRIEF_JSON_SCHEMA: dict = {
    "name": "SceneBrief",
    "schema": {
        "type": "object",
        "properties": {
            "objects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "why_interesting": {"type": "string"},
                    },
                    "required": ["name", "why_interesting"],
                    "additionalProperties": False,
                },
            },
            "candidate_variables": {"type": "array", "items": {"type": "string"}},
            "sam_prompts": {"type": "array", "items": {"type": "string"}},
            "suggested_domain": {"type": "string"},
            "narration": {"type": "string"},
        },
        "required": [
            "objects",
            "candidate_variables",
            "sam_prompts",
            "suggested_domain",
            "narration",
        ],
        "additionalProperties": False,
    },
}


def load_pendulum_fixture() -> SceneBrief:
    if OBSERVER_FIXTURE_PENDULUM.is_file():
        data = json.loads(OBSERVER_FIXTURE_PENDULUM.read_text(encoding="utf-8"))
        return SceneBrief.model_validate(data)
    return SceneBrief(
        objects=[SceneObject(name="pendulum bob", why_interesting="periodic motion")],
        candidate_variables=["angle", "length", "period"],
        sam_prompts=["pendulum bob", "A4 sheet"],
        suggested_domain="mechanics.pendulum",
        narration="Default pendulum fixture.",
    )


def _fallback_brief(message: str) -> SceneBrief:
    brief = load_pendulum_fixture()
    brief.narration = message
    return brief


def _read_session_video(session: Session) -> tuple[bytes, str] | None:
    if not session.filename:
        return None
    path = Path(session.filename)
    if not path.is_file():
        return None
    return path.read_bytes(), path.name


def _event(session: Session, stage: str, message: str) -> None:
    session.events.append({"stage": stage, "message": message})


async def run_observer(session: Session, settings: Settings | None = None) -> Session:
    """Run OBSERVE step; updates session.scene and persists to store."""
    settings = settings or get_settings()
    router = ModelRouter(settings, session_id=session.id)
    session.status = SessionStatus.observing
    _event(session, "observe", "Watching the clip — naming objects and variables")

    if session.mode == "fixture" or not router.enabled:
        session.scene = load_pendulum_fixture()
        session.meta_calls.append({"model": "fixture", "kind": "observer", "ok": True})
        return store.put(session)

    domain = session.domain_hint or "mechanics.pendulum"
    prompt = (
        "You are HYPATIA's Observer (Muse Spark). Watch the clip and return SceneBrief JSON: "
        "objects, candidate_variables, sam_prompts for SAM 3.1 open-vocabulary tracking, "
        f"suggested_domain, and plain-language narration. Domain hint: {domain}."
    )
    instructions = "Return only valid JSON matching the schema."

    file_id: str | None = session.video_file_id
    video = _read_session_video(session)
    if video and not file_id:
        data, name = video
        try:
            file_id, upload_log = router.upload_video_bytes(data, name)
            session.video_file_id = file_id
            session.meta_calls.append(upload_log)
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append(
                {"model": "files", "kind": "files.create", "ok": False, "error": str(exc)[:200]}
            )

    try:
        text, log = router.observe_scene(
            prompt=prompt,
            instructions=instructions,
            json_schema=SCENE_BRIEF_JSON_SCHEMA,
            file_id=file_id,
        )
        session.meta_calls.append(log)
        session.scene = SceneBrief.model_validate(json.loads(text))
    except Exception as exc:  # noqa: BLE001
        _event(session, "observe", f"Live Observer failed ({exc}); using fixture scene")
        session.mode = "hybrid"
        session.scene = _fallback_brief("Fallback scene brief after live Observer error.")

    return store.put(session)
