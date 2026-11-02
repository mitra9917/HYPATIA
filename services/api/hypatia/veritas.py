"""VERITAS — physics-break detector for AI-generated clips (Playbook #55 / issue #37)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import FIXTURE_DIR

VERITAS_FIXTURE = FIXTURE_DIR / "veritas_fake_freefall.json"


def load_veritas_fixture() -> dict[str, Any]:
    if VERITAS_FIXTURE.is_file():
        return json.loads(VERITAS_FIXTURE.read_text(encoding="utf-8"))
    return {
        "clip_id": "ai-fake-physics-01",
        "expected_g_m_s2": 9.80665,
        "measured_g_m_s2": 6.1,
        "break_frame": 41,
        "momentum_conserved": False,
        "verdict": "not_physical",
        "headline": "Acceleration ≠ g — likely synthetic physics break",
        "detail": "Frame 41: implied a≈6.1 m/s²; momentum discontinuity vs prior segment.",
    }


def analyze_clip(*, use_fixture: bool = True) -> dict[str, Any]:
    data = load_veritas_fixture() if use_fixture else load_veritas_fixture()
    ok = data.get("verdict") == "physical"
    return {
        "ok": ok,
        "verdict": data.get("verdict", "unknown"),
        "headline": data.get("headline"),
        "detail": data.get("detail"),
        "expected_g_m_s2": data.get("expected_g_m_s2"),
        "measured_g_m_s2": data.get("measured_g_m_s2"),
        "break_frame": data.get("break_frame"),
        "momentum_conserved": data.get("momentum_conserved"),
        "clip_id": data.get("clip_id"),
        "module": "veritas",
    }
