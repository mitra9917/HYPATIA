#!/usr/bin/env python3
"""Smoke-test Glimmer swarm provider (stub always; modal after deploy)."""

from __future__ import annotations

import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "services", "api"))

from hypatia.config import get_settings  # noqa: E402
from hypatia.glimmer import run_glimmer_swarm  # noqa: E402


def main() -> int:
    settings = get_settings()
    provider = settings.glimmer_provider
    print(f"GLIMMER_PROVIDER={provider}")

    try:
        out = run_glimmer_swarm(settings, n=5, domain="mechanics.pendulum")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        if provider == "modal":
            print(
                "Hint: deploy first — modal deploy services/api/modal_app.py "
                "(Playbook #50 / #39). Until then use GLIMMER_PROVIDER=stub in .env."
            )
        return 1

    candidates = out.get("candidates") or []
    print(f"ok provider={out.get('provider')} candidates={len(candidates)} latency_ms={out.get('latency_ms', 'n/a')}")
    for c in candidates[:3]:
        print(f"  - {c.get('form', c)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
