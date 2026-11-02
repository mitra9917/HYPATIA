"""Equation DSL + SciPy symbolic fitter for pendulum laws (P2.1 / Playbook #29, issue #19).

PySR is optional (heavy); CI uses SciPy curve_fit on declared law forms.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit

from .models import TrajectoryPoint

G = 9.80665

try:
    from pysr import PySRRegressor  # type: ignore[import-untyped]

    _HAS_PYSR = True
except ImportError:
    _HAS_PYSR = False


@dataclass(frozen=True)
class LawForm:
    """Human-readable law + parameter names for fitting."""

    id: str
    form_latex: str
    form_plain: str
    param_names: tuple[str, ...]


PENDULUM_PERIOD = LawForm(
    id="pendulum_period",
    form_latex=r"T = 2\pi\sqrt{L/g}",
    form_plain="Small-angle pendulum period",
    param_names=("g",),
)

PENDULUM_SHM = LawForm(
    id="pendulum_shm",
    form_latex=r"\theta(t) = A\cos(\omega t + \phi)",
    form_plain="SHM angle waveform",
    param_names=("A", "omega", "phi"),
)


def _angle_arrays(points: list[TrajectoryPoint]) -> tuple[np.ndarray, np.ndarray]:
    ts = np.array([p.t for p in points if p.angle_rad is not None], dtype=float)
    angs = np.array([p.angle_rad for p in points if p.angle_rad is not None], dtype=float)
    return ts, angs


def recover_g_from_period(period_s: float, length_m: float) -> float:
    """Invert T = 2π√(L/g) → g = 4π²L / T²."""
    return (4 * math.pi**2 * length_m) / max(period_s**2, 1e-9)


def fit_g_period_law(points: list[TrajectoryPoint], length_m: float) -> dict[str, float]:
    from .science import estimate_period

    period = estimate_period(points)
    if period is None or period <= 0:
        period = 2 * math.pi * math.sqrt(length_m / G)
    g_hat = recover_g_from_period(period, length_m)
    return {"g": float(g_hat), "L": float(length_m), "T": float(period)}


def _shm(t: np.ndarray, a: float, omega: float, phi: float) -> np.ndarray:
    return a * np.cos(omega * t + phi)


def fit_g_shm_law(points: list[TrajectoryPoint], length_m: float) -> dict[str, float]:
    ts, angs = _angle_arrays(points)
    if len(ts) < 12:
        return fit_g_period_law(points, length_m)
    amp0 = float(np.max(np.abs(angs)) + 1e-6)
    p0 = (amp0, math.sqrt(G / max(length_m, 1e-6)), 0.0)
    try:
        (a_hat, omega_hat, phi_hat), _ = curve_fit(
            _shm,
            ts,
            angs,
            p0=p0,
            bounds=([0, 0, -2 * math.pi], [2.0, 50.0, 2 * math.pi]),
            maxfev=8000,
        )
    except (RuntimeError, ValueError):
        return fit_g_period_law(points, length_m)
    g_hat = float(omega_hat**2 * length_m)
    return {
        "A": float(a_hat),
        "omega": float(omega_hat),
        "phi": float(phi_hat),
        "g": g_hat,
        "L": float(length_m),
    }


def fit_pendulum_g(points: list[TrajectoryPoint], length_m: float) -> dict[str, float]:
    """Best-effort g recovery: SHM fit, falling back to period inversion."""
    shm = fit_g_shm_law(points, length_m)
    period = fit_g_period_law(points, length_m)
    # Prefer SHM when enough samples; average for stability
    g_blend = 0.65 * shm["g"] + 0.35 * period["g"]
    return {
        "g": float(g_blend),
        "L": float(length_m),
        "g_shm": shm["g"],
        "g_period": period["g"],
        "T": period.get("T", 0.0),
    }


def optional_pysr_g(
    points: list[TrajectoryPoint],
    length_m: float,
    *,
    niterations: int = 20,
) -> dict[str, float] | None:
    """Optional PySR search for θ(t); returns None if PySR not installed."""
    if not _HAS_PYSR:
        return None
    ts, angs = _angle_arrays(points)
    if len(ts) < 20:
        return None
    x = ts.reshape(-1, 1)
    reg = PySRRegressor(
        niterations=niterations,
        binary_operators=["+", "-", "*"],
        unary_operators=["cos", "sin"],
        maxsize=20,
        populations=8,
        progress=False,
        verbosity=0,
    )
    reg.fit(x, angs)
    # Still report SciPy g — PySR is exploratory pre-screen only in P2.1
    return {"pysr_equation": str(reg.sympy()), "g": fit_pendulum_g(points, length_m)["g"], "L": length_m}


def law_catalog() -> list[LawForm]:
    return [PENDULUM_PERIOD, PENDULUM_SHM]
