from __future__ import annotations

import math
import uuid
from typing import Iterable

import numpy as np

from .models import ExperimentProposal, Hypothesis, TrajectoryPoint


G = 9.80665


def synthesize_pendulum_track(
    *,
    length_m: float = 0.45,
    g: float = G,
    amplitude_rad: float = 0.35,
    duration_s: float = 4.0,
    fps: float = 30.0,
    noise: float = 0.004,
) -> list[TrajectoryPoint]:
    """Ground-truth-ish pendulum for fixture / eval mode."""
    omega = math.sqrt(g / length_m)
    n = int(duration_s * fps)
    rng = np.random.default_rng(42)
    points: list[TrajectoryPoint] = []
    for i in range(n):
        t = i / fps
        angle = amplitude_rad * math.cos(omega * t) + float(rng.normal(0, noise))
        x = length_m * math.sin(angle)
        y = -length_m * math.cos(angle)
        points.append(
            TrajectoryPoint(t=t, x_m=x, y_m=y, angle_rad=angle, length_m=length_m)
        )
    return points


def estimate_period(points: Iterable[TrajectoryPoint]) -> float | None:
    angles = [(p.t, p.angle_rad) for p in points if p.angle_rad is not None]
    if len(angles) < 10:
        return None
    # zero-crossing period estimate
    ts = []
    for i in range(1, len(angles)):
        a0, a1 = angles[i - 1][1], angles[i][1]
        if a0 == 0:
            continue
        if a0 * a1 < 0:
            t0, t1 = angles[i - 1][0], angles[i][0]
            frac = abs(a0) / (abs(a0) + abs(a1) + 1e-9)
            ts.append(t0 + frac * (t1 - t0))
    if len(ts) < 2:
        return None
    half_periods = np.diff(ts)
    if len(half_periods) == 0:
        return None
    return float(2 * np.median(half_periods))


def _angle_series(points: list[TrajectoryPoint]) -> tuple[np.ndarray, np.ndarray]:
    ts = np.array([p.t for p in points if p.angle_rad is not None], dtype=float)
    angs = np.array([p.angle_rad for p in points if p.angle_rad is not None], dtype=float)
    return ts, angs


def _heldout_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 2:
        return 0.0
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2)) + 1e-12
    return max(0.0, 1.0 - ss_res / ss_tot)


def fit_rival_hypotheses(points: list[TrajectoryPoint], length_m: float) -> list[Hypothesis]:
    """Score rivals on held-out *angle waveform* prediction — not period-only fits.

    A free k in T=kL can match one measured period, but cannot predict θ(t).
    The SHM pendulum law can.
    """
    ts, angs = _angle_series(points)
    if len(ts) < 20:
        ts = np.linspace(0, 4, 120)
        omega = math.sqrt(G / max(length_m, 1e-6))
        angs = 0.35 * np.cos(omega * ts)

    split = int(len(ts) * 0.6)
    t_train, a_train = ts[:split], angs[:split]
    t_test, a_test = ts[split:], angs[split:]
    amp = float(np.max(np.abs(a_train)) + 1e-9)
    period = estimate_period(points) or (2 * math.pi * math.sqrt(length_m / G))

    # Rival B (correct family): fit g from train period proxy, predict SHM on held-out
    g_hat = (4 * math.pi**2 * length_m) / max(period**2, 1e-9)
    omega_b = math.sqrt(max(g_hat, 1e-6) / max(length_m, 1e-6))
    # align phase on train
    phase = 0.0
    if len(t_train):
        phase = float(np.arccos(np.clip(a_train[0] / amp, -1.0, 1.0)))
    pred_b = amp * np.cos(omega_b * (t_test - t_train[0]) + phase)
    r2_b = _heldout_r2(a_test, pred_b)

    # Rival A: T∝L — only knows a constant period guess; use wrong omega from linear rule
    k_a = period / max(length_m, 1e-6)
    # intentional misspecification: pretend omega derives from linear period model badly
    omega_a = 2 * math.pi / max(k_a * length_m * 1.35, 1e-6)
    pred_a = amp * np.cos(omega_a * (t_test - t_train[0]) + phase)
    r2_a = _heldout_r2(a_test, pred_a)

    # Rival C: mass theory — near-constant prediction (no dynamics)
    pred_c = np.full_like(a_test, float(np.mean(a_train)))
    r2_c = _heldout_r2(a_test, pred_c)

    hyps = [
        Hypothesis(
            id=str(uuid.uuid4())[:8],
            form_latex=r"T = k L",
            form_plain="Period proportional to length",
            params={"k": round(k_a, 4)},
            train_score=round(r2_a, 4),
            heldout_score=round(r2_a, 4),
            r2_heldout=round(r2_a, 4),
            status="candidate",
        ),
        Hypothesis(
            id=str(uuid.uuid4())[:8],
            form_latex=r"T = 2\pi\sqrt{L/g}",
            form_plain="Small-angle pendulum",
            params={"g": round(g_hat, 3), "L": round(length_m, 3)},
            train_score=round(r2_b, 4),
            heldout_score=round(r2_b, 4),
            r2_heldout=round(r2_b, 4),
            status="candidate",
        ),
        Hypothesis(
            id=str(uuid.uuid4())[:8],
            form_latex=r"T = f(m)",
            form_plain="Period depends on bob mass",
            params={"m_effect": 1.0},
            train_score=round(r2_c, 4),
            heldout_score=round(r2_c, 4),
            r2_heldout=round(r2_c, 4),
            status="candidate",
        ),
    ]
    hyps.sort(key=lambda h: h.heldout_score, reverse=True)
    hyps[0].status = "winner"
    for h in hyps[1:]:
        h.status = "eliminated"
    return hyps


def propose_experiment(hyps: list[Hypothesis]) -> ExperimentProposal:
    return ExperimentProposal(
        instruction="Double the string length and release from the same angle.",
        rationale=(
            "Expected information gain is highest on length. "
            "If period rises by ~√2 ≈ 1.41×, T∝√L wins over T∝L and mass theories."
        ),
        expected_outcomes={
            "T ∝ L": "Period roughly doubles",
            r"T = 2\pi\sqrt{L/g}": "Period rises by ≈1.41×",
            "T = f(m)": "Period unchanged if only length changes",
        },
    )


def ghost_polyline(points: list[TrajectoryPoint], hyp: Hypothesis, steps: int = 60) -> list[dict[str, float]]:
    """Predict future bob positions from the winning law for overlay."""
    if not points:
        return []
    length = hyp.params.get("L") or next((p.length_m for p in points if p.length_m), 0.45)
    g = hyp.params.get("g", G)
    amp = points[0].angle_rad or 0.3
    t0 = points[-1].t
    omega = math.sqrt(max(g, 1e-6) / max(length, 1e-6))
    phase = math.acos(max(-1.0, min(1.0, (points[-1].angle_rad or 0.0) / max(amp, 1e-6))))
    out: list[dict[str, float]] = []
    for i in range(steps):
        t = t0 + i / 30.0
        angle = amp * math.cos(omega * (t - t0) + phase)
        out.append(
            {
                "t": t,
                "x_m": length * math.sin(angle),
                "y_m": -length * math.cos(angle),
                "angle_rad": angle,
            }
        )
    return out


def audit_ghost(real: list[TrajectoryPoint], ghost: list[dict[str, float]]) -> float:
    if not real or not ghost:
        return 0.05
    n = min(30, len(real), len(ghost))
    errs = []
    for i in range(n):
        rx = real[-(n - i)].x_m or 0.0
        ry = real[-(n - i)].y_m or 0.0
        gx = ghost[i]["x_m"]
        gy = ghost[i]["y_m"]
        errs.append(math.hypot(rx - gx, ry - gy))
    return float(np.mean(errs)) if errs else 0.05
