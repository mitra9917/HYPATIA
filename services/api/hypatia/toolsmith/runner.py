"""Run promoted Toolsmith code against fixture frames (local subprocess; Modal uses modal_app.toolsmith_run)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..config import FIXTURE_DIR

PROMOTED_PENDULUM_TOOL = """
import json
import sys
from pathlib import Path

def mean_angle_rad(points):
    vals = [p["angle_rad"] for p in points if p.get("angle_rad") is not None]
    return sum(vals) / len(vals) if vals else 0.0

track = json.loads(Path(sys.argv[1]).read_text())
pts = track.get("points") or []
assert len(pts) >= 10, "need at least 10 trajectory samples"
m = mean_angle_rad(pts)
assert abs(m) < 1.5, f"mean angle out of range: {m}"
print(f"ok mean_angle={m:.4f} n={len(pts)}")
"""


def _fixture_track_path() -> Path:
    tracks = sorted((FIXTURE_DIR / "tracks").glob("*_round_pendulum_bob_weight.json"))
    if not tracks:
        raise FileNotFoundError("no pendulum track fixtures under data/fixtures/tracks")
    return tracks[0]


def run_promoted_tool_test(*, track_path: Path | None = None) -> dict[str, Any]:
    """Execute promoted pendulum tool + unit assertions on recorded SAM track JSON."""
    track = track_path or _fixture_track_path()
    with tempfile.TemporaryDirectory() as td:
        tool_path = Path(td) / "pendulum_angle_tool.py"
        tool_path.write_text(PROMOTED_PENDULUM_TOOL.strip() + "\n", encoding="utf-8")
        link = Path(td) / "track.json"
        link.write_text(track.read_text(encoding="utf-8"), encoding="utf-8")
        proc = subprocess.run(
            ["python3", str(tool_path), str(link)],
            cwd=td,
            capture_output=True,
            text=True,
            timeout=30,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONNOUSERSITE": "1"},
        )
        return {
            "tool_id": "pendulum_angle_from_track",
            "track_fixture": track.name,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
            "ok": proc.returncode == 0,
            "sandbox": "local_subprocess",
            "network": False,
        }
