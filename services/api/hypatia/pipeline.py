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
    fit_rival_hypotheses,
    propose_experiment,
    synthesize_pendulum_track,
)
from .observer import run_observer
from .store import store


from .runtime_ops import resolve_fixture_mode


def _event(session: Session, stage: str, message: str) -> None:
    session.events.append({"stage": stage, "message": message})


def _mode_for(settings: Settings) -> str:
    if resolve_fixture_mode(settings):
        return "fixture"
    return "live"


async def create_session(
    *,
    filename: str | None,
    source_type: str,
    raw: bytes | None,
    upload_consent: bool = False,
    consent_version: str = "hypatia-demo-2026",
    domain_hint: str | None = None,
) -> Session:
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
        upload_consent=upload_consent,
        consent_version=consent_version,
        domain_hint=domain_hint,
    )
    if upload_consent:
        from datetime import datetime, timezone

        session.upload_consent = True
        session.consent_at = datetime.now(timezone.utc).isoformat()
    _event(session, "created", f"Session ready in {session.mode} mode")
    session = store.put(session)
    from .pi import library_search_stub

    session.domain_hint = session.domain_hint or "mechanics.pendulum"
    lib = library_search_stub(session)
    if lib.get("matches"):
        session.library_hint = {
            "message": "Prior accepted law in library — compare rivals faster this session.",
            "matches": lib["matches"][:3],
        }
        _event(session, "library", session.library_hint["message"])
        store.put(session)
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
    from .pi import plan_pi_phase

    plan = await plan_pi_phase(session, client, settings, "observe")
    _event(session, "observe", str(plan.get("narration", "Observer pass"))[:240])
    await run_observer(session, settings)


async def _measure(session: Session, client: MetaClient, settings: Settings) -> None:
    from .measurer import run_measurer
    from .pi import plan_pi_phase

    plan = await plan_pi_phase(session, client, settings, "measure")
    _event(session, "measure", str(plan.get("narration", "Measurer pass"))[:240])
    await run_measurer(session, client, settings)


async def _hypothesize(session: Session, client: MetaClient, settings: Settings) -> None:
    from .pi import plan_pi_phase
    from .pi_tools import execute_hypothesize_tools

    session.status = SessionStatus.hypothesizing
    _event(session, "hypothesize", f"Rival theories via {settings.glimmer_provider} swarm + held-out scoring")

    track = session.tracks[0] if session.tracks else None
    points = track.points if track else synthesize_pendulum_track()
    length = next((p.length_m for p in points if p.length_m), 0.45) or 0.45

    plan = await plan_pi_phase(session, client, settings, "hypothesize")
    _event(session, "hypothesize", str(plan.get("narration", "Theorist pass"))[:240])

    try:
        execute_hypothesize_tools(session, settings, plan, points, length)
    except Exception as exc:  # noqa: BLE001
        session.meta_calls.append(
            {
                "model": "muse-glimmer",
                "provider": settings.glimmer_provider,
                "ok": False,
                "error": str(exc)[:200],
            }
        )
        session.hypotheses = fit_rival_hypotheses(points, length)
        _event(session, "hypothesize", f"Tooling fallback ({exc}); fixture rivals only")

    from .scoring_gate import attach_winner_bootstrap_ci

    session.hypotheses = attach_winner_bootstrap_ci(session.hypotheses, points, length)

    store.put(session)


async def _imagine(session: Session, client: MetaClient, settings: Settings) -> None:
    from .imagination_audit import metre_xy_to_bbox_norm, sam_imagination_audit
    from .imagination_media import save_imagination_frame
    from .predictor import forward_polyline, state_at_delta

    session.status = SessionStatus.imagining
    _event(session, "imagine", "Drawing predicted future (Muse Image or geometric ghost)")

    winner = next((h for h in session.hypotheses if h.status == "winner"), None)
    if not winner:
        return
    track = session.tracks[0] if session.tracks else None
    points = track.points if track else []
    ghost = forward_polyline(points, winner)
    audit = sam_imagination_audit(track, points, ghost)
    err = float(audit["audit_error_m"])
    source = "geometric"
    image_bytes: bytes | None = None

    if client.enabled and session.mode == "live":
        try:
            image_bytes, log = client.generate_image(
                f"Scientific visualization of a pendulum bob at the next predicted angle for law {winner.form_latex}"
            )
            session.meta_calls.append(log)
            if image_bytes:
                source = "muse_image"
                _event(
                    session,
                    "imagine",
                    f"Muse Image frame (${log.get('image_spend_usd_est', 0.01):.2f} est.); SAM audit next",
                )
            else:
                source = "geometric"
                _event(session, "imagine", "Muse Image returned empty; geometric ghost fallback")
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append({"model": settings.meta_image_model, "ok": False, "error": str(exc)[:160]})
            source = "geometric"
            _event(session, "imagine", f"Muse Image unavailable ({exc}); geometric ghost fallback")
    else:
        session.meta_calls.append(
            {
                "model": settings.meta_image_model,
                "kind": "images.generate_stub",
                "ok": True,
                "images_generated": 0,
                "image_spend_usd_est": 0.0,
                "note": "fixture geometric ghost",
            }
        )

    if not image_bytes:
        from .imagination_media import render_geometric_frame

        image_bytes = render_geometric_frame(
            [(float(p.x_m), float(p.y_m)) for p in points if p.x_m is not None and p.y_m is not None],
            [(float(g["x_m"]), float(g["y_m"])) for g in ghost],
        )
    frame_uri = save_imagination_frame(session.id, image_bytes, index=0)
    next_state = state_at_delta(points, winner, 0.5)
    length = float(next_state.get("length_m") or winner.params.get("L") or 0.45)
    if track and points:
        length = float(points[-1].length_m or length)
    mask_hint = metre_xy_to_bbox_norm(
        float(next_state["x_m"]),
        float(next_state["y_m"]),
        length_m=length,
    )

    session.imagination = [
        ImaginationFrame(
            hypothesis_id=winner.id,
            predicted_description=f"Ghost trajectory under {winner.form_latex}",
            audit_error_m=round(err, 4),
            ghost_polyline=ghost,
            source=source,
            ghost_frame_uri=frame_uri,
            mask_hint_bbox=mask_hint,
            audit_iou=float(audit.get("audit_iou") or 0.0),
            audit_centroid_m=float(audit.get("audit_centroid_m") or err),
        )
    ]
    _event(
        session,
        "imagine",
        f"SAM audit IoU={audit.get('audit_iou', 0):.3f} centroid={audit.get('audit_centroid_m', err):.4f} m",
    )
    store.put(session)


async def _experiment(session: Session, client: MetaClient, settings: Settings) -> None:
    from .pi import library_search_stub, plan_pi_phase

    session.status = SessionStatus.experimenting
    session.experiment = propose_experiment(session.hypotheses)

    plan = await plan_pi_phase(session, client, settings, "experiment")
    if "library_search" in (plan.get("tools") or []):
        lib = library_search_stub(session)
        session.meta_calls.append(
            {"model": "library", "kind": "library_search", "ok": True, "matches": len(lib.get("matches", []))}
        )
    _event(session, "experiment", str(plan.get("narration", session.experiment.instruction))[:240])
    store.put(session)


async def _accept(session: Session) -> None:
    from .scoring_gate import assert_can_accept_law, bootstrap_g_ci, demo_g_display, track_points_for_session

    assert_can_accept_law(session)
    winner = next((h for h in session.hypotheses if h.status == "winner"), None)
    if not winner:
        return
    points, length_m = track_points_for_session(session)
    if not winner.param_ci.get("g"):
        lo, hi = bootstrap_g_ci(points, length_m)
        winner.param_ci = {"g": [round(lo, 2), round(hi, 2)]}
    g = winner.params.get("g")
    ci = winner.param_ci.get("g") or []
    err_bar = abs((g or 9.8) - 9.80665)
    if len(ci) == 2:
        err_bar = (ci[1] - ci[0]) / 2
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
            f"**Demo:** {demo_g_display(winner)}",
            "",
            f"Parameters: `{winner.params}`",
            f"Train R²: `{winner.train_score:.4f}` · Held-out R²: `{winner.heldout_score:.4f}`",
            "",
            "## Rivals eliminated",
            ", ".join(h.form_latex for h in session.hypotheses if h.status == "eliminated"),
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
        error_bars={"g": round(err_bar, 3)} if g is not None else {},
    )
    _event(session, "accepted", f"Law locked: {demo_g_display(winner)}")
    store.put(session)
