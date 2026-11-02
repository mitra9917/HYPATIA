"""In-process session progress bus for SSE (P1.6 / Playbook #22, issue #15)."""

from __future__ import annotations

import asyncio
import json
import threading
from collections import defaultdict
from typing import Any

_lock = threading.Lock()
_subscribers: dict[str, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)


def format_sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


def publish(session_id: str, event: str, data: dict[str, Any]) -> None:
    """Notify live SSE clients (no-op if nobody is connected)."""
    payload = {"event": event, "data": data}
    with _lock:
        queues = list(_subscribers.get(session_id, ()))
    for queue in queues:
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            pass


def subscribe(session_id: str) -> asyncio.Queue[dict[str, Any]]:
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=64)
    with _lock:
        _subscribers[session_id].add(queue)
    return queue


def unsubscribe(session_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
    with _lock:
        subs = _subscribers.get(session_id)
        if not subs:
            return
        subs.discard(queue)
        if not subs:
            _subscribers.pop(session_id, None)


def reset_subscribers_for_tests() -> None:
    with _lock:
        _subscribers.clear()
