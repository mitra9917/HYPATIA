"""P2.1 symbolic fitter — recover g on synthetic + fixture pendulum (Playbook #29 / #19)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hypatia.models import Track, TrajectoryPoint
from hypatia.science import G, synthesize_pendulum_track
from hypatia.symbolic_fitter import (
    fit_g_period_law,
    fit_g_shm_law,
    fit_pendulum_g,
    law_catalog,
    recover_g_from_period,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_TRACK = ROOT / "data" / "fixtures" / "tracks" / "pendulum_bob_default.json"

G_TOL = 0.75  # m/s² — noise + discrete period estimate


def test_law_catalog_has_pendulum_forms() -> None:
    ids = {law.id for law in law_catalog()}
    assert "pendulum_period" in ids
    assert "pendulum_shm" in ids


def test_recover_g_from_period_inverts_formula() -> None:
    length = 0.45
    period = 2 * 3.14159 * (length / G) ** 0.5
    g_hat = recover_g_from_period(period, length)
    assert abs(g_hat - G) < 0.05


def test_fit_pendulum_g_on_synthetic() -> None:
    points = synthesize_pendulum_track(length_m=0.45, g=G, duration_s=4.0, noise=0.002)
    fit = fit_pendulum_g(points, 0.45)
    assert abs(fit["g"] - G) < G_TOL


def test_fit_g_shm_on_synthetic() -> None:
    points = synthesize_pendulum_track(length_m=0.5, g=9.7, duration_s=3.5, noise=0.003)
    params = fit_g_shm_law(points, 0.5)
    assert abs(params["g"] - 9.7) < G_TOL


def test_fit_g_period_law_on_synthetic() -> None:
    points = synthesize_pendulum_track(length_m=0.4, g=9.81, noise=0.001)
    params = fit_g_period_law(points, 0.4)
    assert abs(params["g"] - 9.81) < G_TOL


@pytest.mark.skipif(not FIXTURE_TRACK.is_file(), reason="fixture track missing")
def test_fit_pendulum_g_on_fixture_track() -> None:
    track = Track.model_validate(json.loads(FIXTURE_TRACK.read_text(encoding="utf-8")))
    length = track.points[0].length_m or 0.45
    fit = fit_pendulum_g(track.points, length)
    assert 8.0 < fit["g"] < 12.0


def test_fit_rival_hypotheses_winner_has_fitted_g() -> None:
    from hypatia.science import fit_rival_hypotheses

    points = synthesize_pendulum_track(length_m=0.45, g=G, duration_s=4.0, noise=0.002)
    hyps = fit_rival_hypotheses(points, 0.45)
    winner = hyps[0]
    assert r"T = 2\pi\sqrt{L/g}" in winner.form_latex or "pendulum" in winner.form_plain.lower()
    assert "g" in winner.params
    assert abs(float(winner.params["g"]) - G) < 1.5
