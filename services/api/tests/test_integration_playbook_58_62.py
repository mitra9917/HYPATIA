"""Playbooks #58–#62 / issues #66, #63, #40, #67, #65 — integration checks."""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_hackathon_submission_artifacts() -> None:
    for rel in (
        "docs/HACKATHON_ALIGNMENT.md",
        "docs/META_EVIDENCE.md",
        "meta_evidence.json",
        "docs/FINALS_WARM.md",
        "scripts/cost_report.py",
        "data/fixtures/cost_report_sample.json",
        "evals/suites/desk-mechanics.json",
        ".github/workflows/warm-health.yml",
    ):
        assert (ROOT / rel).is_file(), rel


def test_readme_mentions_hackathon_alignment() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "HACKATHON_ALIGNMENT" in readme or "hackathon" in readme.lower()
    assert "Meta Global AI Developer Hackathon" in readme


def test_ci_workflow_has_lint_and_fixture_tests() -> None:
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "eslint" in ci
    assert "test_integration_playbook_52_57" in ci or "verify_playbook" in ci
    assert "FIXTURE_MODE" in ci


def test_modal_finals_warm_flag() -> None:
    text = (ROOT / "services/api/modal_app.py").read_text(encoding="utf-8")
    assert "MODAL_FINALS_WARM" in text
    ast.parse(text)


def test_cost_report_script() -> None:
    r = subprocess.run(
        ["python3", str(ROOT / "scripts/cost_report.py"), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["budget_usd"] == 150.0


def test_evals_fixture_run() -> None:
    r = subprocess.run(
        ["python3", "-m", "evals", "--suite", "desk-mechanics", "--mode", "fixture"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr or r.stdout
