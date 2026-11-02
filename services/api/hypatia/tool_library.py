"""Promoted Toolsmith tools persisted in-process (Playbook #53 / issue #35)."""

from __future__ import annotations

from typing import Any

_BUILTIN: list[dict[str, Any]] = [
    {
        "id": "pendulum_angle_from_track",
        "title": "Mean pendulum angle from SAM track JSON",
        "domain": "mechanics.pendulum",
        "promoted": True,
        "source": "toolsmith",
    },
]

_promoted: list[dict[str, Any]] = list(_BUILTIN)


def list_tools() -> list[dict[str, Any]]:
    return list(_promoted)


def promote_tool(entry: dict[str, Any]) -> dict[str, Any]:
    tid = str(entry.get("id") or entry.get("tool_id") or "")
    if not tid:
        raise ValueError("tool id required")
    for existing in _promoted:
        if existing["id"] == tid:
            existing.update(entry)
            return existing
    row = {
        "id": tid,
        "title": entry.get("title") or tid,
        "domain": entry.get("domain") or "general",
        "promoted": True,
        "source": entry.get("source") or "toolsmith",
    }
    _promoted.append(row)
    return row
