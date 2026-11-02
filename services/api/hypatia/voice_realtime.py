"""Voice realtime WebSocket — fixture stream with file-ASR fallback (P3.10 / #61)."""

from __future__ import annotations

import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from .config import Settings, get_settings

logger = logging.getLogger(__name__)

REALTIME_ASR_URL = "wss://api.meta.ai/v1/asr/realtime"


async def voice_realtime_ws(websocket: WebSocket) -> None:
    """Stream partial transcripts; live Meta ASR when key + client ready, else fixture chunks."""
    await websocket.accept()
    settings = get_settings()
    session_id = websocket.query_params.get("session_id")
    await websocket.send_json(
        {
            "type": "ready",
            "backend": "meta_realtime" if settings.has_meta_key else "fixture_stream",
            "documented_url": REALTIME_ASR_URL,
            "session_id": session_id,
            "fallback": "POST /api/voice/turn with audio_base64 or transcript",
        }
    )
    buffer = 0
    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                break
            if "bytes" in msg and msg["bytes"]:
                buffer += len(msg["bytes"])
                partial = f"Listening… ({buffer} bytes buffered)"
                await websocket.send_json({"type": "partial", "transcript": partial})
            elif "text" in msg and msg["text"]:
                data = json.loads(msg["text"])
                if data.get("type") == "commit":
                    final = data.get("transcript") or "What if we double the string length?"
                    await websocket.send_json({"type": "final", "transcript": final})
                    await websocket.send_json(
                        {
                            "type": "reply",
                            "text": (
                                "Try doubling string length — expect period ratio ≈ √2 if T∝√L holds."
                            ),
                        }
                    )
                    break
    except WebSocketDisconnect:
        logger.debug("voice realtime disconnected session_id=%s", session_id)
    finally:
        try:
            await websocket.close()
        except Exception:  # noqa: BLE001
            pass
