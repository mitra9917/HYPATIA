"""Wonder PI orchestration — one plan call per major phase (P2.3 / #21)."""

from __future__ import annotations

import json
from typing import Any

from .config import Settings
from .meta_client import MetaClient
from .models import Session
from .store import store

PI_PHASES = ("observe", "measure", "hypothesize", "experiment")

PI_TOOL_NAMES = (
    "spawn_theorist",
    "run_pysr",
    "library_search",
    "delegate_spark",
    "delegate_sam",
)

PI_PLAN_JSON_SCHEMA: dict[str, Any] = {
    "name": "PIPhasePlan",
    "schema": {
        "type": "object",
        "properties": {
            "phase": {"type": "string"},
            "tools": {
                "type": "array",
                "items": {"type": "string", "enum": list(PI_TOOL_NAMES)},
            },
            "goal": {"type": "string"},
            "narration": {"type": "string"},
        },
        "required": ["phase", "tools", "goal", "narration"],
        "additionalProperties": False,
    },
}


def fixture_pi_plan(phase: str, session: Session) -> dict[str, Any]:
    """Deterministic PI plan for fixture / offline CI (no Wonder call)."""
    domain = session.domain_hint or (
        session.scene.suggested_domain if session.scene else "mechanics.pendulum"
    )
    tools_by_phase: dict[str, list[str]] = {
        "observe": ["delegate_spark"],
        "measure": ["delegate_sam"],
        "hypothesize": ["spawn_theorist", "run_pysr", "library_search"],
        "experiment": ["library_search"],
    }
    narration_by_phase: dict[str, str] = {
        "observe": "Catalog the scene and SAM targets before we measure motion.",
        "measure": "Track the bob trajectory in metres; calibration gates everything else.",
        "hypothesize": "Spawn Glimmer rivals, fit with PySR/SciPy, rank on held-out angles.",
        "experiment": "Pick the experiment that best separates the surviving laws.",
    }
    return {
        "phase": phase,
        "tools": tools_by_phase.get(phase, []),
        "goal": f"Advance {phase} for domain {domain}",
        "narration": narration_by_phase.get(phase, f"Run {phase} stage."),
        "source": "fixture_pi",
    }


def library_search_stub(session: Session) -> dict[str, Any]:
    """Stub prior-law lookup (Toolsmith / library hook)."""
    domain = session.domain_hint or (session.scene.suggested_domain if session.scene else None)
    matches: list[dict[str, Any]] = []
    for sid in store.list_ids():
        other = store.get(sid)
        if not other or not other.notebook or sid == session.id:
            continue
        if domain and other.domain_hint and other.domain_hint != domain:
            continue
        matches.append(
            {
                "session_id": sid,
                "law_latex": other.notebook.law_latex,
                "params": other.notebook.params,
            }
        )
    return {"domain": domain, "matches": matches[:5]}


async def plan_pi_phase(
    session: Session,
    client: MetaClient,
    settings: Settings,
    phase: str,
) -> dict[str, Any]:
    """Wonder PI: at most one Responses call per phase; reuses previous_response_id."""
    if phase not in PI_PHASES:
        raise ValueError(f"unknown PI phase: {phase}")
    if phase in session.pi_plans:
        return session.pi_plans[phase]

    if not client.enabled or session.mode not in {"live", "hybrid"}:
        plan = fixture_pi_plan(phase, session)
        session.pi_plans[phase] = plan
        return plan

    context = {
        "phase": phase,
        "session_id": session.id,
        "domain_hint": session.domain_hint,
        "mode": session.mode,
        "has_tracks": bool(session.tracks),
        "hypothesis_count": len(session.hypotheses),
    }
    instructions = (
        "You are HYPATIA's Principal Investigator (Muse Wonder). "
        "Return a JSON plan listing which tools to run this phase. "
        "Tools: spawn_theorist (Glimmer rivals), run_pysr (symbolic fit), "
        "library_search (prior laws), delegate_spark (Observer), delegate_sam (Measurer). "
        "Maths and held-out scores decide laws — you plan and narrate only."
    )
    text, log = client.respond_text(
        model=settings.meta_pi_model,
        input_payload=(
            f"Plan pipeline phase `{phase}` for this lab session. Context: {json.dumps(context)}"
        ),
        instructions=instructions,
        json_schema=PI_PLAN_JSON_SCHEMA,
        previous_response_id=session.pi_response_id,
    )
    log["role"] = "pi_plan"
    log["phase"] = phase
    session.meta_calls.append(log)
    rid = log.get("response_id")
    if isinstance(rid, str) and rid:
        session.pi_response_id = rid

    plan = json.loads(text)
    plan["source"] = "muse_wonder"
    session.pi_plans[phase] = plan
    return plan


def wonder_plan_calls(session: Session, *, pi_model: str) -> int:
    return sum(
        1
        for row in session.meta_calls
        if row.get("role") == "pi_plan" and row.get("model") == pi_model
    )
