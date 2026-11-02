"""Playbook #36 / issue #22 — held-out gate + bootstrap CI."""

from __future__ import annotations

import os

import pytest

os.environ["FIXTURE_MODE"] = "true"
os.environ["MODEL_API_KEY"] = ""

from hypatia.science import fit_rival_hypotheses, synthesize_pendulum_track  # noqa: E402
from hypatia.scoring_gate import (  # noqa: E402
    attach_winner_bootstrap_ci,
    bootstrap_g_ci,
    demo_g_display,
    held_out_winner_clear,
    law_accept_gate,
)


def test_train_and_heldout_differ_for_misspecified_rival() -> None:
    points = synthesize_pendulum_track(length_m=0.45)
    hyps = fit_rival_hypotheses(points, 0.45)
    winner = next(h for h in hyps if h.status == "winner")
    linear = next(h for h in hyps if h.form_plain.startswith("Period proportional"))
    assert winner.heldout_score > linear.heldout_score
    assert winner.train_score >= 0


def test_bootstrap_ci_bounds_g() -> None:
    points = synthesize_pendulum_track(length_m=0.45)
    lo, hi = bootstrap_g_ci(points, 0.45)
    assert lo < hi
    assert 7.0 < lo < 12.0
    assert 7.0 < hi < 12.0


def test_winner_gets_param_ci() -> None:
    points = synthesize_pendulum_track()
    hyps = attach_winner_bootstrap_ci(fit_rival_hypotheses(points, 0.45), points, 0.45)
    winner = next(h for h in hyps if h.status == "winner")
    assert winner.param_ci.get("g")
    assert demo_g_display(winner).startswith("T = 2π")


def test_law_gate_passes_fixture_pendulum() -> None:
    points = synthesize_pendulum_track()
    hyps = attach_winner_bootstrap_ci(fit_rival_hypotheses(points, 0.45), points, 0.45)
    from hypatia.models import Session

    session = Session(id="t", hypotheses=hyps)
    gate = law_accept_gate(session)
    assert held_out_winner_clear(hyps)
    assert gate["ok"] is True
