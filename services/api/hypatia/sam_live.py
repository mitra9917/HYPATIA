"""Live SAM 3.1 video calls with streaming + meta_sam_parser decode."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from openai import OpenAI

from .config import Settings
from .models import MaskFrame
from .sam_decode import parse_sam_response


def _collect_stream_text(stream: Any) -> str:
    chunks: list[str] = []
    for event in stream:
        etype = getattr(event, "type", None) or (event.get("type") if isinstance(event, dict) else None)
        if etype == "response.output_text.delta":
            delta = getattr(event, "delta", None)
            if delta is None and isinstance(event, dict):
                delta = event.get("delta")
            if delta:
                chunks.append(str(delta))
        elif etype == "response.completed":
            resp = getattr(event, "response", None)
            if resp is not None:
                text = getattr(resp, "output_text", None)
                if text:
                    return str(text)
    return "".join(chunks)


def segment_video_sync(
    client: OpenAI,
    settings: Settings,
    *,
    prompt: str,
    file_id: str,
    media_size: tuple[int, int],
    session_id: str | None = None,
) -> tuple[list[MaskFrame], dict[str, Any]]:
    """Blocking SAM video track: stream=True, decode with meta_sam_parser."""
    started = time.time()
    width, height = media_size
    if not file_id:
        raise ValueError("SAM 3 video segmentation requires Meta Files file_id")

    content: list[dict[str, Any]] = [
        {"type": "input_video", "file_id": file_id},
        {"type": "input_text", "text": prompt},
    ]
    stream = client.responses.create(
        model=settings.meta_sam_model,
        input=[{"role": "user", "content": content}],
        stream=True,
    )
    text = _collect_stream_text(stream)
    masks = parse_sam_response(text, width=width, height=height)
    log: dict[str, Any] = {
        "model": settings.meta_sam_model,
        "kind": "sam",
        "ok": True,
        "stream": True,
        "chars": len(text),
        "file_id": file_id,
        "mask_frames": len(masks),
        "latency_ms": int((time.time() - started) * 1000),
    }
    if session_id:
        log["session_id"] = session_id
    return masks, log


async def segment_video_async(
    client: OpenAI,
    settings: Settings,
    *,
    prompt: str,
    file_id: str,
    media_size: tuple[int, int],
    session_id: str | None = None,
) -> tuple[list[MaskFrame], dict[str, Any]]:
    return await asyncio.to_thread(
        segment_video_sync,
        client,
        settings,
        prompt=prompt,
        file_id=file_id,
        media_size=media_size,
        session_id=session_id,
    )
