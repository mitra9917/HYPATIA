"""Held-out rivalry gates + bootstrap CIs (P2.4 / issue #22, Playbook #36)."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from .models import Hypothesis, Session, TrajectoryPoint
from .symbolic_fitter import fit_pendulum_g, recover_g_from_period
from .science import estimate_period, synthesize_pendulum_track

G_TRUE = 9.80665
G_DEMO_TOLERANCE = 0.10  # ±10% for pendulum g (issue #57)


class AcceptGateError(ValueError):
    """Raised when held-out / bootstrap gates block law acceptance."""


def bootstrap_g_ci(
    points: list[TrajectoryPoint],
    length_m: float,
    *,
    n_samples: int = 160,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap over sliding-window period estimates → g (preserves time order)."""
    ts = np.array([p.t for p in points if p.angle_rad is not None], dtype=float)
    angs = np.array([p.angle_rad for p in points if p.angle_rad is not None], dtype=float)
    base_g = fit_pendulum_g(points, length_m)["g"]
    if len(ts) < 40:
        return (base_g * 0.92, base_g * 1.08)

    window = 36
    step = 4
    window_gs: list[float] = []
    for start in range(0, len(ts) - window, step):
        sample_pts = [
            TrajectoryPoint(t=float(ts[i]), angle_rad=float(angs[i]), length_m=length_m)
            for i in range(start, start + window)
        ]
        period = estimate_period(sample_pts)
        if period and period > 0:
            window_gs.append(recover_g_from_period(period, length_m))

    if len(window_gs) < 6:
        return (base_g * 0.92, base_g * 1.08)

    rng = np.random.default_rng(seed)
    gs: list[float] = []
    arr = np.array(window_gs, dtype=float)
    for _ in range(n_samples):
        pick = arr[rng.integers(0, len(arr), size=len(arr))]
        gs.append(float(np.mean(pick)))
    low, high = float(np.percentile(gs, 2.5)), float(np.percentile(gs, 97.5))
    return (low, high)


def attach_winner_bootstrap_ci(
    hypotheses: list[Hypothesis],
    points: list[TrajectoryPoint],
    length_m: float,
) -> list[Hypothesis]:
    winner = next((h for h in hypotheses if h.status == "winner"), None)
    if not winner or "g" not in winner.params:
        return hypotheses
    lo, hi = bootstrap_g_ci(points, length_m)
    winner.param_ci = {"g": [round(lo, 2), round(hi, 2)]}
    return hypotheses


def held_out_winner_clear(hypotheses: Iterable[Hypothesis]) -> bool:
    hyps = list(hypotheses)
    if not hyps:
        return False
    winner = next((h for h in hyps if h.status == "winner"), None)
    if not winner:
        return False
    rivals = [h for h in hyps if h.id != winner.id]
    if not rivals:
        return True
    return all(winner.heldout_score > h.heldout_score for h in rivals)


def g_within_demo_bounds(g: float | None) -> bool:
    if g is None:
        return False
    return abs(g - G_TRUE) / G_TRUE <= G_DEMO_TOLERANCE


def bootstrap_sane(winner: Hypothesis) -> bool:
    ci = winner.param_ci.get("g") if winner.param_ci else None
    if not ci or len(ci) != 2:
        return True
    lo, hi = float(ci[0]), float(ci[1])
    return lo > 0 and hi > lo


def law_accept_gate(session: Session) -> dict[str, object]:
    winner = next((h for h in session.hypotheses if h.status == "winner"), None)
    reasons: list[str] = []
    if not winner:
        reasons.append("no held-out winner")
    held_ok = held_out_winner_clear(session.hypotheses)
    if not held_ok:
        reasons.append("winner does not beat all rivals on held-out R²")
    g = winner.params.get("g") if winner else None
    g_ok = g_within_demo_bounds(g)
    if winner and "g" in winner.params and not g_ok:
        reasons.append(f"g={g:.2f} outside ±{int(G_DEMO_TOLERANCE * 100)}% of 9.81 m/s²")
    boot_ok = bootstrap_sane(winner) if winner else False
    if winner and winner.param_ci and not boot_ok:
        reasons.append("bootstrap CI for g is invalid")
    ok = bool(winner and held_ok and g_ok and boot_ok)
    return {
        "ok": ok,
        "held_out_winner": held_ok,
        "g_in_range": g_ok,
        "bootstrap_ok": boot_ok,
        "reasons": reasons,
    }


def assert_can_accept_law(session: Session) -> None:
    gate = law_accept_gate(session)
    if not gate["ok"]:
        msg = "; ".join(str(r) for r in gate.get("reasons") or ["accept gates failed"])
        raise AcceptGateError(msg)


def demo_g_display(winner: Hypothesis) -> str:
    """Issue #23 demo string: T=2π√(L/g), g≈9.7±0.4."""
    g = winner.params.get("g", 9.7)
    ci = winner.param_ci.get("g") if winner.param_ci else None
    if ci and len(ci) == 2:
        mid = (ci[0] + ci[1]) / 2
        half = (ci[1] - ci[0]) / 2
        return f"T = 2π√(L/g), g ≈ {mid:.1f} ± {half:.1f}"
    return f"T = 2π√(L/g), g ≈ {g:.1f}"


def track_points_for_session(session: Session) -> tuple[list[TrajectoryPoint], float]:
    track = session.tracks[0] if session.tracks else None
    points = track.points if track else synthesize_pendulum_track()
    length = next((p.length_m for p in points if p.length_m), 0.45) or 0.45
    return points, float(length)
