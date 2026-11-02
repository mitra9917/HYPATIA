"""Playbooks #50–#51 / issues #47, #49 — integration scaffold tests."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_modal_app_references_volume_and_secret() -> None:
    text = (ROOT / "services/api/modal_app.py").read_text()
    assert "hypatia-weights" in text
    assert "hypatia-secrets" in text
    ast.parse(text)


def test_modal_integration_doc_exists() -> None:
    doc = ROOT / "docs/MODAL_INTEGRATION.md"
    assert doc.is_file()
    body = doc.read_text()
    assert "hypatia-secrets" in body
    assert "hypatia-weights" in body


def test_github_actions_secrets_doc_and_workflow() -> None:
    doc = ROOT / "docs/GITHUB_ACTIONS_SECRETS.md"
    wf = ROOT / ".github/workflows/deploy.yml"
    assert doc.is_file() and wf.is_file()
    assert "MODAL_TOKEN_ID" in doc.read_text()
    assert "MODAL_TOKEN_ID" in wf.read_text()


def test_verify_scripts_exit_zero() -> None:
    for script in ("verify_modal_integration.sh", "verify_github_actions_secrets.sh"):
        r = subprocess.run(["bash", str(ROOT / "scripts" / script)], cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr or r.stdout
