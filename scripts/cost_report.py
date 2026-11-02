#!/usr/bin/env python3
"""Aggregate Meta API spend from session meta_calls (Playbook #61 / issue #67)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "fixtures" / "cost_report_sample.json"

# Hackathon envelope (~$150 credits) — rough public pricing for narrative only
SPARK_USD_PER_1M_TOKENS = 0.35
SAM_USD_PER_1K_FRAMES = 0.20
IMAGE_USD_EACH = 0.01
VOICE_USD_PER_HOUR = 0.18
WONDER_USD_PER_1M_TOKENS = 2.50
BUDGET_USD = 150.0


def _estimate_row(row: dict) -> float:
    kind = str(row.get("kind", ""))
    model = str(row.get("model", ""))
    if row.get("image_spend_usd_est") is not None:
        return float(row["image_spend_usd_est"])
    tokens = int(row.get("tokens") or row.get("total_tokens") or 0)
    frames = int(row.get("frames") or 0)
    latency_ms = int(row.get("latency_ms") or 0)
    if "sam" in model.lower() or kind == "sam":
        return (frames / 1000.0) * SAM_USD_PER_1K_FRAMES if frames else 0.02
    if "image" in model.lower() or kind == "image":
        return IMAGE_USD_EACH
    if "voice" in model.lower() or kind == "voice":
        return (latency_ms / 3_600_000.0) * VOICE_USD_PER_HOUR
    if "wonder" in model.lower() or kind == "pi":
        return (tokens / 1_000_000.0) * WONDER_USD_PER_1M_TOKENS if tokens else 0.005
    if tokens:
        return (tokens / 1_000_000.0) * SPARK_USD_PER_1M_TOKENS
    if row.get("ok") and row.get("model") not in ("fixture", "library"):
        return 0.001
    return 0.0


def aggregate_sessions(sessions: list[dict]) -> dict:
    by_model: dict[str, float] = {}
    by_kind: dict[str, float] = {}
    total = 0.0
    calls = 0
    for sess in sessions:
        for row in sess.get("meta_calls") or []:
            calls += 1
            usd = _estimate_row(row)
            total += usd
            model = str(row.get("model", "unknown"))
            kind = str(row.get("kind", "other"))
            by_model[model] = by_model.get(model, 0.0) + usd
            by_kind[kind] = by_kind.get(kind, 0.0) + usd
    return {
        "sessions": len(sessions),
        "meta_calls": calls,
        "estimated_usd": round(total, 4),
        "budget_usd": BUDGET_USD,
        "budget_remaining_usd": round(BUDGET_USD - total, 2),
        "by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda x: -x[1])},
        "by_kind": {k: round(v, 4) for k, v in sorted(by_kind.items(), key=lambda x: -x[1])},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=SAMPLE, help="JSON list of session snapshots")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "sessions" in data:
        sessions = data["sessions"]
    elif isinstance(data, list):
        sessions = data
    else:
        raise SystemExit("input must be a list of sessions or {sessions: [...]}")
    report = aggregate_sessions(sessions)
    if args.json:
        print(json.dumps(report, indent=2))
        return
    print("HYPATIA Meta API cost report (estimate)")
    print(f"  sessions: {report['sessions']}")
    print(f"  meta_calls: {report['meta_calls']}")
    print(f"  estimated spend: ${report['estimated_usd']:.4f}")
    print(f"  hackathon envelope: ${report['budget_usd']:.0f} (remaining ~${report['budget_remaining_usd']:.2f})")
    print("  by_model:", report["by_model"])
    print("  by_kind:", report["by_kind"])


if __name__ == "__main__":
    main()
