#!/usr/bin/env python3
"""Smoke-test Meta Model API connectivity. Opt-in: requires MODEL_API_KEY."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "api"))

from hypatia.config import get_settings  # noqa: E402
from hypatia.meta_client import MetaClient  # noqa: E402


def main() -> int:
    settings = get_settings()
    if not settings.has_meta_key:
        print("MODEL_API_KEY missing — skip live smoke (fixture mode still works).")
        return 0
    client = MetaClient(settings)
    result = client.health_ping()
    print(result)
    return 0 if result.get("meta") else 1


if __name__ == "__main__":
    raise SystemExit(main())
