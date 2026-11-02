from __future__ import annotations

import uuid
from pathlib import Path

from .config import MEDIA_DIR, Settings, get_settings
from .meta_client import MetaClient, upload_bytes_to_s3
from .meta_files import ensure_session_video_file_id, primary_video_file_id
from .model_router import ModelRouter
from .models import (
    ImaginationFrame,
    Notebook,
    Session,
    SessionStatus,
)
from .science import (
    audit_ghost,
    fit_rival_hypotheses,
    ghost_polyline,
    propose_experiment,
    synthesize_pendulum_track,
)
from .observer import run_observer
from .store import store


def _event(session: Session, stage: str, message: str) -> None:
    session.events.append({"stage": stage, "message": message})


def _mode_for(settings: Settings) -> str:
    if settings.effective_fixture_mode:
        return "fixture"
    return "live"


async def create_session(*, filename: str | None, source_type: str, raw: bytes | None) -> Session:
    settings = get_settings()
    sid = str(uuid.uuid4())
    path = None
    if raw is not None and filename:
        dest = MEDIA_DIR / f"{sid}_{Path(filename).name}"
        dest.write_bytes(raw)
        path = str(dest)
        try:
            await upload_bytes_to_s3(settings, f"uploads/{sid}/{Path(filename).name}", raw, "video/mp4")
        except Exception:  # noqa: BLE001
            # S3 is optional; misconfigured AWS must not break session create.
            pass

    session = Session(
        id=sid,
        status=SessionStatus.created,
        source_type=source_type,
        filename=path or filename,
        mode=_mode_for(settings),
    )
    _event(session, "created", f"Session ready in {session.mode} mode")
    session = store.put(session)
    if path and session.mode == "live":
        router = ModelRouter(settings, session_id=sid)
        try:
            ensure_session_video_file_id(session, router, settings=settings)
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append(
                {"model": "files", "kind": "files.create", "ok": False, "error": str(exc)[:200]}
            )
        store.put(session)
    return session


async def run_full_pipeline(session_id: str, domain_hint: str | None = None) -> Session:
    from .orchestrator import run_full_pipeline_orchestrated

    return await run_full_pipeline_orchestrated(session_id, domain_hint=domain_hint)


async def _observe(session: Session, client: MetaClient, settings: Settings) -> None:
    await run_observer(session, settings)


async def _measure(session: Session, client: MetaClient, settings: Settings) -> None:
    from .measurer import run_measurer

    await run_measurer(session, client, settings)


async def _hypothesize(session: Session, client: MetaClient, settings: Settings) -> None:
    session.status = SessionStatus.hypothesizing
    _event(session, "hypothesize", f"Rival theories via {settings.glimmer_provider} swarm + held-out scoring")

    track = session.tracks[0] if session.tracks else None
    points = track.points if track else synthesize_pendulum_track()
    length = next((p.length_m for p in points if p.length_m), 0.45) or 0.45
    session.hypotheses = fit_rival_hypotheses(points, length)

    if client.enabled and session.mode in {"live", "hybrid"}:
        try:
            winner = next(h for h in session.hypotheses if h.status == "winner")
            text, log = client.respond_text(
                model=settings.meta_pi_model,
                input_payload=(
                    "You are HYPATIA's Principal Investigator. Briefly confirm why "
                    f"this law wins on held-out prediction: {winner.form_latex} params={winner.params}"
                ),
                instructions="Reply in 2 short sentences for the lab notebook.",
            )
            session.meta_calls.append(log)
            _event(session, "hypothesize", text.strip()[:240])
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append({"model": settings.meta_pi_model, "ok": False, "error": str(exc)[:160]})

    store.put(session)


async def _imagine(session: Session, client: MetaClient, settings: Settings) -> None:
    session.status = SessionStatus.imagining
    _event(session, "imagine", "Drawing predicted future (Muse Image or geometric ghost)")

    winner = next((h for h in session.hypotheses if h.status == "winner"), None)
    if not winner:
        return
    points = session.tracks[0].points if session.tracks else []
    ghost = ghost_polyline(points, winner)
    err = audit_ghost(points, ghost)
    source = "geometric"

    if client.enabled and session.mode == "live":
        try:
            _, log = client.generate_image(
                f"Scientific visualization of a pendulum bob at the next predicted angle for law {winner.form_latex}"
            )
            session.meta_calls.append(log)
            source = "muse_image"
            _event(session, "imagine", "Muse Image frame generated; SAM-style audit on geometric proxy")
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append({"model": settings.meta_image_model, "ok": False, "error": str(exc)[:160]})
            _event(session, "imagine", f"Muse Image unavailable ({exc}); geometric ghost")

    session.imagination = [
        ImaginationFrame(
            hypothesis_id=winner.id,
            predicted_description=f"Ghost trajectory under {winner.form_latex}",
            audit_error_m=round(err, 4),
            ghost_polyline=ghost,
            source=source,
        )
    ]
    store.put(session)


async def _experiment(session: Session, client: MetaClient, settings: Settings) -> None:
    session.status = SessionStatus.experimenting
    session.experiment = propose_experiment(session.hypotheses)
    _event(session, "experiment", session.experiment.instruction)

    if client.enabled and session.mode in {"live", "hybrid"}:
        try:
            text, log = client.respond_text(
                model=settings.meta_pi_model,
                input_payload=(
                    "Phrase this next experiment for a student in one spoken sentence: "
                    + session.experiment.instruction
                ),
            )
            session.meta_calls.append(log)
            _event(session, "experiment", text.strip()[:240])
        except Exception:  # noqa: BLE001
            pass
    store.put(session)


async def _accept(session: Session) -> None:
    winner = next((h for h in session.hypotheses if h.status == "winner"), None)
    if not winner:
        return
    g = winner.params.get("g")
    err = abs((g or 9.8) - 9.80665)
    md = "\n".join(
        [
            f"# HYPATIA Lab Notebook — session `{session.id}`",
            "",
            f"**Mode:** {session.mode}",
            f"**Domain:** {session.domain_hint}",
            "",
            "## Accepted law",
            f"$${' '.join(winner.form_latex)}$$",
            "",
            f"Parameters: `{winner.params}`",
            f"Held-out score: `{winner.heldout_score:.4f}`",
            "",
            "## Next experiment",
            session.experiment.instruction if session.experiment else "n/a",
            "",
            "## Meta calls",
            f"{len(session.meta_calls)} logged",
            "",
            "_LLM proposes, maths decides. Law accepted only via held-out rivalry._",
        ]
    )
    session.notebook = Notebook(
        markdown=md,
        law_latex=winner.form_latex,
        params=winner.params,
        error_bars={"g": round(err, 3)} if g is not None else {},
    )
    _event(session, "accepted", f"Law locked: {winner.form_plain}")
    store.put(session)
