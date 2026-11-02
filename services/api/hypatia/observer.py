"""Observer agent — Muse Spark → SceneBrief (P1.3 / Playbook #17, issue #12)."""

from __future__ import annotations

import json
from pathlib import Path

from .config import FIXTURE_DIR, Settings, get_settings
from .meta_files import ensure_session_video_file_id, primary_video_file_id
from .model_router import ModelRouter
from .models import SceneBrief, SceneObject, Session, SessionStatus
from .store import store

OBSERVER_FIXTURE_PENDULUM = FIXTURE_DIR / "observer_pendulum.json"
OBSERVER_FIXTURE_CELLS = FIXTURE_DIR / "observer_cells.json"

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


def load_cells_fixture() -> SceneBrief:
    if OBSERVER_FIXTURE_CELLS.is_file():
        data = json.loads(OBSERVER_FIXTURE_CELLS.read_text(encoding="utf-8"))
        return SceneBrief.model_validate(data)
    return SceneBrief(
        objects=[SceneObject(name="cell_colony", why_interesting="logistic growth")],
        candidate_variables=["colony_area", "doubling_time"],
        sam_prompts=["bright cell colony cluster"],
        suggested_domain="biology.cells",
        narration="Default cell timelapse fixture.",
    )


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


def load_observer_fixture(session: Session) -> SceneBrief:
    hint = (session.domain_hint or "").lower()
    if "cell" in hint or hint.startswith("biology"):
        return load_cells_fixture()
    return load_pendulum_fixture()


def _fallback_brief(message: str) -> SceneBrief:
    brief = load_pendulum_fixture()
    brief.narration = message
    return brief


def _event(session: Session, stage: str, message: str) -> None:
    session.events.append({"stage": stage, "message": message})


async def run_observer(session: Session, settings: Settings | None = None) -> Session:
    """Run OBSERVE step; updates session.scene and persists to store."""
    settings = settings or get_settings()
    router = ModelRouter(settings, session_id=session.id)
    session.status = SessionStatus.observing
    _event(session, "observe", "Watching the clip — naming objects and variables")

    if session.mode == "fixture" or not router.enabled:
        session.scene = load_observer_fixture(session)
        session.meta_calls.append({"model": "fixture", "kind": "observer", "ok": True})
        return store.put(session)

    domain = session.domain_hint or "mechanics.pendulum"
    prompt = (
        "You are HYPATIA's Observer (Muse Spark). Watch the clip and return SceneBrief JSON: "
        "objects, candidate_variables, sam_prompts for SAM 3.1 open-vocabulary tracking, "
        f"suggested_domain, and plain-language narration. Domain hint: {domain}."
    )
    instructions = "Return only valid JSON matching the schema."

    try:
        ensure_session_video_file_id(session, router, settings=settings)
    except Exception as exc:  # noqa: BLE001
        session.meta_calls.append(
            {"model": "files", "kind": "files.create", "ok": False, "error": str(exc)[:200]}
        )

    file_id = primary_video_file_id(session)

    try:
        text, log = router.observe_scene(
            prompt=prompt,
            instructions=instructions,
            json_schema=SCENE_BRIEF_JSON_SCHEMA,
            file_id=file_id,
        )
        session.meta_calls.append(log)
        session.scene = SceneBrief.model_validate(json.loads(text))
        if settings.fixture_record and session.scene:
            from .fixture_recorder import write_observer_fixture

            write_observer_fixture(session.scene)
            _event(session, "Recorded Observer SceneBrief to data/fixtures/")
    except Exception as exc:  # noqa: BLE001
        _event(session, "observe", f"Live Observer failed ({exc}); using fixture scene")
        session.mode = "hybrid"
        session.scene = _fallback_brief("Fallback scene brief after live Observer error.")

    return store.put(session)
