"""Video corpus SOURCES.md gate (P1.8 / Playbook #28, issue #17)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / "data" / "videos" / "SOURCES.md"
MIN_CLIPS = 8


def _count_catalog_rows(text: str) -> int:
    rows = 0
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*---", line):
            continue
        if "| ID |" in line or "| File |" in line:
            continue
        rows += 1
    return rows


def test_sources_md_lists_at_least_eight_clips() -> None:
    assert SOURCES.is_file(), "data/videos/SOURCES.md missing"
    n = _count_catalog_rows(SOURCES.read_text(encoding="utf-8"))
    assert n >= MIN_CLIPS, f"expected ≥{MIN_CLIPS} clips, found {n}"
