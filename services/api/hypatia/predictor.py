"""Kinematic / SHM forward predictor for ghost pipeline (P3.1 / Playbook #31, issue #26)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .models import Hypothesis, TrajectoryPoint
from .science import G


@dataclass(frozen=True)
class PendulumState:
    """Small-angle pendulum state at time t."""

    t: float
    angle_rad: float
    length_m: float
    omega: float
    amplitude: float
    phase: float
    t_anchor: float

    def at(self, t: float) -> PendulumState:
        angle = self.amplitude * math.cos(self.omega * (t - self.t_anchor) + self.phase)
        return PendulumState(
            t=t,
            angle_rad=angle,
            length_m=self.length_m,
            omega=self.omega,
            amplitude=self.amplitude,
            phase=self.phase,
            t_anchor=self.t_anchor,
        )

    def advance(self, dt: float) -> PendulumState:
        return self.at(self.t + dt)

    def to_point(self) -> dict[str, float]:
        return {
            "t": self.t,
            "x_m": self.length_m * math.sin(self.angle_rad),
            "y_m": -self.length_m * math.cos(self.angle_rad),
            "angle_rad": self.angle_rad,
            "length_m": self.length_m,
        }


def initial_state(points: list[TrajectoryPoint], hyp: Hypothesis) -> PendulumState:
    if not points:
        length = float(hyp.params.get("L", 0.45))
        g = float(hyp.params.get("g", G))
        omega = math.sqrt(max(g, 1e-6) / max(length, 1e-6))
        return PendulumState(
            t=0.0,
            angle_rad=0.3,
            length_m=length,
            omega=omega,
            amplitude=0.3,
            phase=0.0,
            t_anchor=0.0,
        )
    length = float(
        hyp.params.get("L") or next((p.length_m for p in points if p.length_m), 0.45) or 0.45
    )
    g = float(hyp.params.get("g", G))
    omega = math.sqrt(max(g, 1e-6) / max(length, 1e-6))
    amp = max(abs(points[0].angle_rad or 0.3), 1e-6)
    last = points[-1]
    t_anchor = last.t
    angle_last = last.angle_rad or amp
    phase = math.acos(max(-1.0, min(1.0, angle_last / amp)))
    return PendulumState(
        t=t_anchor,
        angle_rad=angle_last,
        length_m=length,
        omega=omega,
        amplitude=amp,
        phase=phase,
        t_anchor=t_anchor,
    )


def forward_polyline(
    points: list[TrajectoryPoint],
    hyp: Hypothesis,
    *,
    steps: int = 60,
    fps: float = 30.0,
) -> list[dict[str, float]]:
    """Predict bob states from t₀ through t₀ + steps/fps (ghost overlay path)."""
    state = initial_state(points, hyp)
    out: list[dict[str, float]] = []
    for i in range(steps):
        t = state.t + i / fps
        out.append(state.at(t).to_point())
    return out


def state_at_delta(
    points: list[TrajectoryPoint],
    hyp: Hypothesis,
    delta_s: float,
) -> dict[str, float]:
    """state(t+Δ) for single-step ghost / mask hints."""
    state = initial_state(points, hyp)
    return state.advance(delta_s).to_point()
