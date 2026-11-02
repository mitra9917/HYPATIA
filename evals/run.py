"""Fixture eval harness (Playbook #60 / EVALS.md). No live Meta in default mode."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals" / "results"
SUITES = ROOT / "evals" / "suites"


def run_suite(name: str, *, mode: str = "fixture") -> dict:
    path = SUITES / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"unknown suite: {name} ({path})")
    spec = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for clip in spec.get("clips", []):
        rows.append(
            {
                "clip_id": clip["id"],
                "true_law": clip.get("true_law"),
                "recovered_fixture": clip.get("recovered_fixture", "T=2π√(L/g)"),
                "g_or_key": clip.get("g_or_key", "9.8 ± 0.4 m/s²"),
                "mode": mode,
                "active_experiments": clip.get("active_experiments", 1),
                "ghost_mae_m": clip.get("ghost_mae_m", 0.012),
                "held_out_pass": clip.get("held_out_pass", True),
            }
        )
    return {
        "suite": name,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clips": rows,
        "summary": {
            "count": len(rows),
            "held_out_pass_rate": sum(1 for r in rows if r["held_out_pass"]) / max(len(rows), 1),
        },
    }


def write_results(payload: dict) -> tuple[Path, Path]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    json_path = RESULTS / f"{stamp}.json"
    md_path = RESULTS / f"{stamp}_summary.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# HYPATIA eval summary — {payload['suite']} ({payload['mode']})",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "| Clip | True law | Recovered (fixture) | Key const | Ghost MAE (m) | Held-out |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in payload["clips"]:
        lines.append(
            f"| {r['clip_id']} | {r['true_law']} | {r['recovered_fixture']} | {r['g_or_key']} | {r.get('ghost_mae_m') if r.get('ghost_mae_m') is not None else '—'} | {r['held_out_pass']} |"
        )
    lines.extend(
        [
            "",
            f"**Held-out pass rate:** {payload['summary']['held_out_pass_rate']:.0%}",
            "",
            "_Fixture rows — run with `--mode live` only via explicit opt-in outside CI._",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="HYPATIA eval harness")
    parser.add_argument("--suite", default="desk-mechanics")
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    args = parser.parse_args()
    if args.mode == "live":
        raise SystemExit("live eval requires scripts/smoke_meta_api.py — not run in CI")
    payload = run_suite(args.suite, mode=args.mode)
    j, m = write_results(payload)
    print(f"wrote {j}")
    print(f"wrote {m}")


if __name__ == "__main__":
    main()
