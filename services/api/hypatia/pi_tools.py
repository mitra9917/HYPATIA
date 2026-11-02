"""Execute PI tool delegations after Wonder plans a phase."""

from __future__ import annotations

from typing import Any

from .config import Settings
from .models import Session, TrajectoryPoint
from .pi import library_search_stub
from .science import fit_rival_hypotheses
from .symbolic_fitter import fit_pendulum_g as _pysr_path_g
from .theorist import run_theorist_swarm_and_score


def execute_hypothesize_tools(
    session: Session,
    settings: Settings,
    plan: dict[str, Any],
    points: list[TrajectoryPoint],
    length_m: float,
) -> None:
    tools = plan.get("tools") or ["spawn_theorist", "run_pysr"]
    swarm: dict[str, Any] | None = None

    if "library_search" in tools:
        lib = library_search_stub(session)
        session.meta_calls.append(
            {"model": "library", "kind": "library_search", "ok": True, "matches": len(lib.get("matches", []))}
        )

    if "spawn_theorist" in tools:
        session.hypotheses, swarm, glimmer_log = run_theorist_swarm_and_score(
            settings,
            points,
            length_m,
            domain_hint=session.domain_hint,
        )
        session.meta_calls.append(glimmer_log)
    else:
        session.hypotheses = fit_rival_hypotheses(points, length_m)

    if "run_pysr" in tools:
        fit = _pysr_path_g(points, length_m)
        session.meta_calls.append(
            {
                "model": "pysr",
                "kind": "run_pysr",
                "ok": True,
                "g": round(fit["g"], 4),
                "note": "SciPy/symbolic path (PySR optional locally)",
            }
        )
        winner = next((h for h in session.hypotheses if h.status == "winner"), None)
        if winner and "g" in fit:
            winner.params = {**winner.params, "g": round(float(fit["g"]), 3)}

    if swarm:
        ids = [c.get("form_id") for c in swarm.get("candidates", [])[:5]]
        session.events.append(
            {
                "stage": "hypothesize",
                "message": f"Glimmer ({swarm.get('provider')}): {len(swarm.get('candidates', []))} rivals "
                f"pre-screened → held-out gate ({', '.join(str(i) for i in ids if i)})",
            }
        )
