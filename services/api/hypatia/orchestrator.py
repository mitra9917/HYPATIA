"""E2E pipeline stage machine — ARCHITECTURE §4 (P1.16 / Playbook #16, issue #56)."""

from __future__ import annotations

from .config import Settings, get_settings
from .meta_client import MetaClient
from .models import Session, SessionStatus
from .observer import run_observer
from .pipeline import (
    _accept,
    _experiment,
    _hypothesize,
    _imagine,
    _measure,
)
from .store import store

# Ordered science loop (matches ARCHITECTURE §4)
PIPELINE_STAGES: tuple[str, ...] = (
    "observe",
    "measure",
    "hypothesize",
    "imagine",
    "experiment",
    "accept",
)

STAGE_TO_STATUS: dict[str, SessionStatus] = {
    "observe": SessionStatus.observing,
    "measure": SessionStatus.measuring,
    "hypothesize": SessionStatus.hypothesizing,
    "imagine": SessionStatus.imagining,
    "experiment": SessionStatus.experimenting,
    "accept": SessionStatus.accepted,
}


class StageGuardError(ValueError):
    """Raised when prerequisites for a pipeline stage are not met."""

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(message)


def assert_stage_prerequisites(session: Session, stage: str) -> None:
    if stage not in PIPELINE_STAGES:
        raise StageGuardError(stage, f"unknown stage: {stage}")

    if stage == "observe":
        return

    if session.scene is None:
        raise StageGuardError(stage, "observe must complete before later stages (scene missing)")

    if stage == "measure":
        return

    if not session.tracks:
        raise StageGuardError(stage, "measure must complete before hypothesize (tracks missing)")

    if stage == "hypothesize":
        return

    if not session.hypotheses:
        raise StageGuardError(stage, "hypothesize must complete before imagine (hypotheses missing)")

    if stage == "imagine":
        return

    if not session.imagination:
        raise StageGuardError(stage, "imagine must complete before experiment (imagination missing)")

    if stage == "experiment":
        return

    if session.experiment is None:
        raise StageGuardError(stage, "experiment must complete before accept (proposal missing)")


async def run_pipeline_stage(
    session_id: str,
    stage: str,
    *,
    settings: Settings | None = None,
) -> Session:
    """Run a single idempotent stage; updates session status and persists."""
    settings = settings or get_settings()
    session = store.get(session_id)
    if not session:
        raise KeyError(session_id)

    assert_stage_prerequisites(session, stage)
    client = MetaClient(settings, session_id=session_id)

    session.error = None
    if session.status == SessionStatus.failed:
        session.status = STAGE_TO_STATUS.get(stage, session.status)

    try:
        if stage == "observe":
            session = await run_observer(session, settings)
        elif stage == "measure":
            await _measure(session, client, settings)
            session = store.get(session_id) or session
        elif stage == "hypothesize":
            await _hypothesize(session, client, settings)
            session = store.get(session_id) or session
        elif stage == "imagine":
            await _imagine(session, client, settings)
            session = store.get(session_id) or session
        elif stage == "experiment":
            await _experiment(session, client, settings)
            session = store.get(session_id) or session
        elif stage == "accept":
            await _accept(session)
            session = store.get(session_id) or session
            session.status = SessionStatus.accepted
        else:
            raise StageGuardError(stage, f"unknown stage: {stage}")
    except StageGuardError:
        raise
    except Exception as exc:  # noqa: BLE001
        session = store.get(session_id) or session
        session.status = SessionStatus.failed
        session.error = str(exc)
        session.events.append({"stage": "failed", "message": str(exc)[:240]})
        return store.put(session)

    return store.put(session)


async def run_pipeline_from(
    session_id: str,
    start_stage: str,
    *,
    domain_hint: str | None = None,
) -> Session:
    """Resume or partial run from ``start_stage`` through ``accept``."""
    if start_stage not in PIPELINE_STAGES:
        raise StageGuardError(start_stage, f"unknown stage: {start_stage}")

    session = store.get(session_id)
    if not session:
        raise KeyError(session_id)
    if domain_hint:
        session.domain_hint = domain_hint
        store.put(session)

    start_idx = PIPELINE_STAGES.index(start_stage)
    session = store.get(session_id) or session
    for stage in PIPELINE_STAGES[start_idx:]:
        session = await run_pipeline_stage(session_id, stage)
        if session.status == SessionStatus.failed:
            break
    return session


async def run_full_pipeline_orchestrated(
    session_id: str,
    domain_hint: str | None = None,
) -> Session:
    return await run_pipeline_from(session_id, "observe", domain_hint=domain_hint)
