#!/usr/bin/env python3
"""Record Observer + SAM slice into data/fixtures/ after a live session (Playbook #23 / #18).

Usage:
  FIXTURE_MODE=false FIXTURE_RECORD=true MODEL_API_KEY=... \\
    python3 scripts/record_fixture_slice.py [--session-id UUID]

Without --session-id, creates a fixture session and runs observe → measure only.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))

from hypatia.config import get_settings  # noqa: E402
from hypatia.fixture_recorder import record_session_slice  # noqa: E402
from hypatia.orchestrator import run_pipeline_stage  # noqa: E402
from hypatia.pipeline import create_session  # noqa: E402
from hypatia.store import init_store, store  # noqa: E402


async def _run(session_id: str) -> dict[str, str]:
    await run_pipeline_stage(session_id, "observe")
    await run_pipeline_stage(session_id, "measure")
    session = store.get(session_id)
    if not session:
        raise RuntimeError("session missing after measure")
    return record_session_slice(session, promote_canonical=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Record Observer + SAM fixtures from a live session")
    parser.add_argument("--session-id", help="Existing session id (else creates fixture upload session)")
    args = parser.parse_args()

    os.environ.setdefault("FIXTURE_RECORD", "true")
    get_settings.cache_clear()
    settings = get_settings()
    init_store(settings)

    if settings.effective_fixture_mode:
        print("Set FIXTURE_MODE=false and MODEL_API_KEY for live Meta capture.", file=sys.stderr)
        sys.exit(1)
    if not settings.fixture_record:
        print("Set FIXTURE_RECORD=true to write under data/fixtures/.", file=sys.stderr)
        sys.exit(1)

    if args.session_id:
        session_id = args.session_id
        if not store.get(session_id):
            print(f"Unknown session {session_id}", file=sys.stderr)
            sys.exit(1)
    else:
        session = await create_session(filename="pendulum.mp4", source_type="fixture", raw=None)
        session.mode = "live"
        store.put(session)
        session_id = session.id
        print(f"Created session {session_id}")

    paths = await _run(session_id)
    print("Recorded:")
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    asyncio.run(main())
