#!/usr/bin/env python3
"""Live Muse Wonder PI smoke (opt-in). Requires MODEL_API_KEY in .env."""

from __future__ import annotations

import asyncio
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "services", "api"))

from hypatia.config import get_settings  # noqa: E402
from hypatia.meta_client import MetaClient  # noqa: E402
from hypatia.models import Session, SessionStatus  # noqa: E402
from hypatia.pi import plan_pi_phase, wonder_plan_calls  # noqa: E402


async def main() -> int:
    settings = get_settings()
    if not settings.has_meta_key:
        print("SKIP: set MODEL_API_KEY in .env for live Wonder PI smoke")
        return 0

    session = Session(id="smoke-pi", status=SessionStatus.created, mode="live")
    client = MetaClient(settings, session_id=session.id)
    print(f"Wonder model={settings.meta_pi_model}")

    try:
        plan = await plan_pi_phase(session, client, settings, "observe")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1

    print(f"ok phase={plan.get('phase')} tools={plan.get('tools')}")
    print(f"narration={str(plan.get('narration', ''))[:120]}…")
    print(f"pi_response_id={session.pi_response_id}")
    print(f"wonder_calls={wonder_plan_calls(session, pi_model=settings.meta_pi_model)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
