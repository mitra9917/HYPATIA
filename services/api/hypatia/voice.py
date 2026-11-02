"""Muse Voice turn — transcribe + PI reply (P3.7 / #32, Playbook #43)."""

from __future__ import annotations

from .config import Settings
from .meta_client import MetaClient
from .models import Session
from .pi import plan_pi_phase


async def voice_turn(
    *,
    settings: Settings,
    session: Session | None,
    transcript: str | None,
    audio_base64: str | None,
) -> dict[str, object]:
    client = MetaClient(settings, session_id=session.id if session else None)
    text = (transcript or "").strip()
    meta_log: dict[str, object] = {"model": settings.meta_voice_model, "kind": "voice.turn", "ok": True}

    if audio_base64 and client.enabled:
        text, vlog = client.transcribe_audio_base64(audio_base64)
        meta_log = vlog
    elif not text:
        text = "What experiment should we run next to distinguish the rivals?"

    reply = (
        "Double the string length and compare the period ratio to √2. "
        "That discriminates T∝√L from T∝L and mass-only theories."
    )
    if session and client.enabled:
        try:
            plan = await plan_pi_phase(session, client, settings, "experiment")
            reply = str(plan.get("narration") or reply)[:500]
        except Exception as exc:  # noqa: BLE001
            meta_log = {**meta_log, "pi_fallback": str(exc)[:120]}
    elif session:
        if session.experiment:
            reply = f"{session.experiment.instruction} — {session.experiment.rationale}"

    if session:
        session.meta_calls.append(meta_log)
        session.events.append({"stage": "voice", "message": f"Q: {text[:120]} → {reply[:120]}"})

    return {
        "transcript": text,
        "reply": reply,
        "meta": meta_log,
        "fixture_mode": settings.effective_fixture_mode,
    }
