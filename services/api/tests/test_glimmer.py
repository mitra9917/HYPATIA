"""P2.2 Glimmer swarm adapter — stub batch + theorist wiring (Playbook #30 / #20)."""

from __future__ import annotations

import pytest

from hypatia.config import Settings
from hypatia.glimmer import (
    MIN_RIVAL_FORMS,
    glimmer_call_log,
    normalize_candidate,
    run_glimmer_swarm,
    run_theorist_batch,
)
from hypatia.science import G, synthesize_pendulum_track
from hypatia.theorist import run_theorist_swarm_and_score


def test_stub_swarm_returns_at_least_three_rivals() -> None:
    settings = Settings(glimmer_provider="stub")
    out = run_glimmer_swarm(settings, n=3, domain="mechanics.pendulum")
    assert out["provider"] == "stub"
    assert len(out["candidates"]) >= MIN_RIVAL_FORMS
    ids = {c["form_id"] for c in out["candidates"]}
    assert "pendulum_period" in ids
    assert "linear_length" in ids
    assert "mass_dependent" in ids


def test_theorist_batch_enforces_minimum() -> None:
    settings = Settings(glimmer_provider="stub")
    batch = run_theorist_batch(settings, n=8)
    assert len(batch["candidates"]) >= MIN_RIVAL_FORMS


def test_normalize_candidate_adds_latex() -> None:
    raw = {"form": "T = k*L", "prior": 0.2}
    norm = normalize_candidate(raw)
    assert norm["form_id"] == "linear_length"
    assert "form_latex" in norm
    assert norm["form_plain"]


def test_glimmer_call_log_shape() -> None:
    settings = Settings(glimmer_provider="stub")
    swarm = run_glimmer_swarm(settings, n=5)
    log = glimmer_call_log(swarm)
    assert log["model"] == "muse-glimmer"
    assert log["ok"] is True
    assert log["candidates"] >= MIN_RIVAL_FORMS


def test_swarm_then_score_picks_pendulum_winner() -> None:
    settings = Settings(glimmer_provider="stub")
    points = synthesize_pendulum_track(length_m=0.45, g=G, noise=0.002)
    hyps, swarm, log = run_theorist_swarm_and_score(settings, points, 0.45)
    assert log["ok"]
    assert len(swarm["candidates"]) >= MIN_RIVAL_FORMS
    winner = hyps[0]
    assert winner.status == "winner"
    assert "\\sqrt" in winner.form_latex or "\\pi" in winner.form_latex
    assert "g" in winner.params


def test_unknown_provider_raises() -> None:
    settings = Settings(glimmer_provider="invalid")
    with pytest.raises(ValueError, match="Unknown GLIMMER_PROVIDER"):
        run_glimmer_swarm(settings)
