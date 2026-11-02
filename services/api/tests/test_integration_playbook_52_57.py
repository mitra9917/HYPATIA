"""Playbooks #52–#57 / issues #34–#37, #64, #39 — integration scaffold tests."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_toolsmith_module_and_modal_hook() -> None:
    runner = ROOT / "services/api/hypatia/toolsmith/runner.py"
    modal = ROOT / "services/api/modal_app.py"
    assert runner.is_file()
    assert "run_promoted_tool_test" in runner.read_text()
    assert "toolsmith_run" in modal.read_text()
    ast.parse(runner.read_text())


def test_phase4_docs_exist() -> None:
    for rel in (
        "docs/DEMO_RELIABILITY.md",
        "docs/PRODUCTION_DEPLOY_CHECKLIST.md",
        "data/fixtures/observer_cells.json",
        "data/fixtures/veritas_fake_freefall.json",
    ):
        assert (ROOT / rel).is_file(), rel


def test_verify_production_deploy_checklist_script() -> None:
    r = subprocess.run(
        ["bash", str(ROOT / "scripts" / "verify_production_deploy_checklist.sh")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr or r.stdout
