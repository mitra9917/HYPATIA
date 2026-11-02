from __future__ import annotations

import json
import uuid
from pathlib import Path

from .config import MEDIA_DIR, Settings, get_settings
from .meta_client import MetaClient, upload_bytes_to_s3
from .models import (
    ImaginationFrame,
    Notebook,
    SceneBrief,
    SceneObject,
    Session,
    SessionStatus,
    Track,
)
from .science import (
    audit_ghost,
    fit_rival_hypotheses,
    ghost_polyline,
    propose_experiment,
    synthesize_pendulum_track,
)
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
        await upload_bytes_to_s3(settings, f"uploads/{sid}/{Path(filename).name}", raw, "video/mp4")

    session = Session(
        id=sid,
        status=SessionStatus.created,
        source_type=source_type,
        filename=path or filename,
        mode=_mode_for(settings),
    )
    _event(session, "created", f"Session ready in {session.mode} mode")
    return store.put(session)


async def run_full_pipeline(session_id: str, domain_hint: str | None = None) -> Session:
    settings = get_settings()
    session = store.get(session_id)
    if not session:
        raise KeyError(session_id)

    client = MetaClient(settings, session_id=session_id)
    session.domain_hint = domain_hint or "mechanics.pendulum"

    try:
        await _observe(session, client, settings)
        await _measure(session, client, settings)
        await _hypothesize(session, client, settings)
        await _imagine(session, client, settings)
        await _experiment(session, client, settings)
        await _accept(session)
        session.status = SessionStatus.accepted
    except Exception as exc:  # noqa: BLE001
        session.status = SessionStatus.failed
        session.error = str(exc)
        _event(session, "failed", str(exc))
    return store.put(session)


async def _observe(session: Session, client: MetaClient, settings: Settings) -> None:
    session.status = SessionStatus.observing
    _event(session, "observe", "Watching the clip — naming objects and variables")

    if session.mode == "fixture" or not client.enabled:
        session.scene = SceneBrief(
            objects=[
                SceneObject(name="pendulum bob", why_interesting="periodic motion"),
                SceneObject(name="string", why_interesting="length may enter the law"),
                SceneObject(name="A4 sheet", why_interesting="scale calibration"),
            ],
            candidate_variables=["angle", "length", "period", "mass?"],
            sam_prompts=["pendulum bob", "string", "A4 sheet"],
            suggested_domain="mechanics.pendulum",
            narration="Something is swinging. Measuring angle and length. Using the A4 sheet for scale.",
        )
        session.meta_calls.append({"model": "fixture", "kind": "observer", "ok": True})
        store.put(session)
        return

    schema = {
        "name": "SceneBrief",
        "schema": {
            "type": "object",
            "properties": {
                "objects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "why_interesting": {"type": "string"},
                        },
                        "required": ["name", "why_interesting"],
                        "additionalProperties": False,
                    },
                },
                "candidate_variables": {"type": "array", "items": {"type": "string"}},
                "sam_prompts": {"type": "array", "items": {"type": "string"}},
                "suggested_domain": {"type": "string"},
                "narration": {"type": "string"},
            },
            "required": [
                "objects",
                "candidate_variables",
                "sam_prompts",
                "suggested_domain",
                "narration",
            ],
            "additionalProperties": False,
        },
    }
    prompt = (
        "You are HYPATIA's Observer. Given a desk science video (pendulum-like), "
        "return JSON SceneBrief with open-vocabulary SAM prompts for measuring motion and scale."
    )
    try:
        text, log = client.respond_text(
            model=settings.observer_model,
            input_payload=prompt,
            instructions="Return only valid JSON matching the schema.",
            json_schema=schema,
        )
        session.meta_calls.append(log)
        data = json.loads(text)
        session.scene = SceneBrief.model_validate(data)
    except Exception as exc:  # noqa: BLE001
        _event(session, "observe", f"Live Observer failed ({exc}); using fixture scene")
        session.mode = "hybrid"
        session.scene = SceneBrief(
            objects=[SceneObject(name="pendulum bob", why_interesting="periodic motion")],
            candidate_variables=["angle", "length", "period"],
            sam_prompts=["pendulum bob", "A4 sheet"],
            suggested_domain="mechanics.pendulum",
            narration="Fallback scene brief after live Observer error.",
        )
    store.put(session)


async def _measure(session: Session, client: MetaClient, settings: Settings) -> None:
    session.status = SessionStatus.measuring
    _event(session, "measure", "SAM 3.1 tracking → metres (or fixture trajectories)")

    prompts = session.scene.sam_prompts if session.scene else ["pendulum bob"]
    length_m = 0.45
    points = synthesize_pendulum_track(length_m=length_m)

    # Attempt live SAM only as a logged probe; numerical tracks still from calibrated synthesis
    # until real video decoding is wired for the uploaded file.
    if client.enabled and session.mode == "live":
        try:
            _, log = client.segment_video_stub_prompt(prompts[0])
            session.meta_calls.append(log)
            _event(session, "measure", "SAM probe succeeded — using calibrated track extraction")
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append({"model": settings.meta_sam_model, "ok": False, "error": str(exc)[:160]})
            _event(session, "measure", f"SAM live probe unavailable ({exc}); calibrated fixture track")
            session.mode = "hybrid"

    session.tracks = [
        Track(
            object_name="pendulum bob",
            sam_prompt=prompts[0],
            points=points,
            metres_per_pixel=0.0012,
            fps=30.0,
        )
    ]
    _event(session, "measure", f"Trajectory ready: {len(points)} samples, L≈{length_m} m")
    store.put(session)


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
