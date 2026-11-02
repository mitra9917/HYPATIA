"""Theorist batch: Glimmer rivals → maths-held-out scoring (P2.2 / Playbook #30)."""

from __future__ import annotations

from typing import Any

from .config import Settings
from .glimmer import glimmer_call_log, run_theorist_batch
from .models import Hypothesis, TrajectoryPoint
from .science import fit_rival_hypotheses


def domain_for_session(domain_hint: str | None) -> str:
    if not domain_hint:
        return "mechanics.pendulum"
    if domain_hint.startswith("mechanics"):
        return domain_hint
    return f"mechanics.{domain_hint}"


def run_theorist_swarm_and_score(
    settings: Settings,
    points: list[TrajectoryPoint],
    length_m: float,
    *,
    domain_hint: str | None = None,
    swarm_n: int = 8,
) -> tuple[list[Hypothesis], dict[str, Any], dict[str, Any]]:
    """Pre-screen rivals with Glimmer, then let held-out scoring pick the winner."""
    domain = domain_for_session(domain_hint)
    swarm = run_theorist_batch(settings, domain=domain, n=swarm_n)
    log = glimmer_call_log(swarm)
    hyps = fit_rival_hypotheses(points, length_m)
    _attach_glimmer_priors(hyps, swarm)
    return hyps, swarm, log


def _attach_glimmer_priors(hyps: list[Hypothesis], swarm: dict[str, Any]) -> None:
    """Copy Glimmer prior into params when form families match (UI / notebook hint)."""
    priors_by_id = {
        str(c.get("form_id")): float(c.get("prior", 0))
        for c in swarm.get("candidates", [])
        if c.get("form_id")
    }
    latex_to_id = {
        str(c.get("form_latex")): str(c.get("form_id"))
        for c in swarm.get("candidates", [])
        if c.get("form_latex")
    }
    for h in hyps:
        fid = latex_to_id.get(h.form_latex)
        if fid and fid in priors_by_id:
            h.params = {**h.params, "glimmer_prior": round(priors_by_id[fid], 3)}
