#!/usr/bin/env python3
"""Smoke-test Meta Model API connectivity. Opt-in: requires MODEL_API_KEY."""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "api"))

from hypatia.config import get_settings  # noqa: E402
from hypatia.model_router import ModelRouter  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Meta Model API smoke")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also ping Wonder (PI) with a one-line prompt (uses extra tokens)",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.has_meta_key:
        print("MODEL_API_KEY missing — skip live smoke (fixture mode still works).")
        return 0

    router = ModelRouter(settings, session_id="smoke")
    ping = router.health_ping()
    print("ping", ping)
    if not ping.get("meta"):
        return 1

    if args.full:
        text, log = router.pi_narrate(
            "Reply with exactly: wonder-ok",
            instructions="Health smoke for Muse Wonder. One token reply only.",
        )
        print("wonder", {"text": text.strip()[:80], "log": log})
        assert "model" in log and "latency_ms" in log
        if settings.model_api_key in json.dumps(log):
            print("FAIL: log leaked API key material")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
