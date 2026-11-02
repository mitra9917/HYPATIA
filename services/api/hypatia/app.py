from __future__ import annotations

import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse

from pydantic import BaseModel

from .config import get_settings
from .contributor_policy import contributor_policy_summary
from .glimmer import run_glimmer_swarm
from .imagination_media import imagination_frame_path
from .meta_client import MetaClient
from .models import CreateSessionResponse, ExperimentResult, RunResponse, Session
from .orchestrator import PIPELINE_STAGES, StageGuardError, run_pipeline_from, run_pipeline_stage
from .notebook_export import build_notebook_export
from .pipeline import create_session, run_full_pipeline
from .runtime_ops import OpsMode, ops_mode_summary, resolve_fixture_mode, set_ops_mode
from .scoring_gate import law_accept_gate
from .science import propose_experiment
from .session_events import format_sse, subscribe, unsubscribe
from .store import init_store, store, store_kind
from .voice import voice_turn
from .voice_realtime import voice_realtime_ws

settings = get_settings()


def enrich_session(session: Session) -> Session:
    return session.model_copy(update={"law_gate": law_accept_gate(session)})


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_store(settings)
    yield


app = FastAPI(
    title="HYPATIA API",
    description="The camera that does science — Meta Model API + partner open weights",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _run_stage(session_id: str, stage: str) -> RunResponse:
    try:
        session = await run_pipeline_stage(session_id, stage)
    except StageGuardError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    return RunResponse(session=enrich_session(session))


@app.get("/api/health")
def health() -> dict:
    client = MetaClient(settings)
    glimmer_probe: dict = {"configured": settings.glimmer_provider}
    try:
        if settings.glimmer_provider == "stub":
            g = run_glimmer_swarm(settings, n=3)
            glimmer_probe = {"ok": True, "provider": g.get("provider"), "candidates": len(g.get("candidates", []))}
    except Exception as exc:  # noqa: BLE001
        glimmer_probe = {"ok": False, "provider": settings.glimmer_provider, "error": str(exc)[:200]}
    ops = ops_mode_summary(settings)
    return {
        "ok": True,
        "service": "hypatia-api",
        "fixture_mode": ops["fixture_mode"],
        "replay_mode": ops["fixture_mode"],
        "ops": ops,
        "fixture_record": settings.fixture_record,
        "model_router": settings.model_router(),
        "contributor_policy": contributor_policy_summary(settings),
        "pipeline_stages": list(PIPELINE_STAGES),
        "glimmer_provider": settings.glimmer_provider,
        "glimmer": glimmer_probe,
        "meta": client.health_ping() if settings.has_meta_key else {"meta": False, "reason": "no key"},
        "s3_configured": bool(settings.s3_bucket and settings.aws_access_key_id),
        "database_configured": bool(settings.database_url.strip()),
        "session_store": store_kind(),
        "deploy_priority": ["meta_model_api", "modal", "baseten", "fireworks", "aws"],
    }


@app.post("/api/sessions", response_model=CreateSessionResponse)
async def post_session(
    file: UploadFile | None = File(default=None),
    source_type: str | None = Form(default=None),
    upload_consent: str = Form(default="false"),
    consent_version: str = Form(default="hypatia-demo-2026"),
) -> CreateSessionResponse:
    raw = await file.read() if file is not None else None
    filename = file.filename if file is not None else "webcam-or-fixture"
    if file is None:
        source = "fixture"
    elif source_type in ("webcam", "upload"):
        source = source_type
    else:
        source = "upload"
    if source in ("upload", "webcam") and upload_consent.lower() not in ("true", "1", "yes"):
        raise HTTPException(
            status_code=422,
            detail="Upload/webcam requires ethics consent (upload_consent=true).",
        )
    consent_ok = upload_consent.lower() in ("true", "1", "yes") or source == "fixture"
    session = await create_session(
        filename=filename,
        source_type=source,
        raw=raw,
        upload_consent=consent_ok,
        consent_version=consent_version,
    )
    return CreateSessionResponse(session=session)


class OpsModeBody(BaseModel):
    mode: OpsMode


@app.post("/api/ops/mode")
def post_ops_mode(body: OpsModeBody) -> dict:
    """Flip fixture ↔ live ↔ hybrid without redeploy (Playbook #45 / #33)."""
    if body.mode in (OpsMode.live, OpsMode.hybrid) and not settings.has_meta_key:
        raise HTTPException(status_code=422, detail="MODEL_API_KEY required for live/hybrid ops mode")
    set_ops_mode(body.mode)
    return ops_mode_summary(get_settings())


@app.get("/api/sessions/{session_id}/notebook.md")
def get_notebook_markdown(session_id: str) -> PlainTextResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if not session.notebook:
        raise HTTPException(422, detail="accept law before notebook export")
    text = build_notebook_export(session)
    headers = {"Content-Disposition": f'attachment; filename="hypatia-{session_id[:8]}-notebook.md"'}
    return PlainTextResponse(text, media_type="text/markdown; charset=utf-8", headers=headers)


@app.websocket("/api/voice/realtime")
async def voice_realtime(websocket: WebSocket) -> None:
    await voice_realtime_ws(websocket)


@app.get("/api/sessions/{session_id}/imagination/{index}/frame.png")
def get_imagination_frame(session_id: str, index: int = 0) -> FileResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    path = imagination_frame_path(session_id, index)
    if not path.is_file():
        raise HTTPException(404, "ghost frame not available — run imagine first")
    return FileResponse(path, media_type="image/png")


@app.get("/api/sessions/{session_id}/tracks/{track_index}/trajectory.csv")
def get_track_trajectory_csv(session_id: str, track_index: int = 0) -> PlainTextResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if track_index < 0 or track_index >= len(session.tracks):
        raise HTTPException(404, "track not found")
    track = session.tracks[track_index]
    if not track.trajectory_csv:
        raise HTTPException(404, "trajectory CSV not available — run measure first")
    return PlainTextResponse(track.trajectory_csv, media_type="text/csv")


@app.get("/api/sessions/{session_id}", response_model=Session)
def get_session(session_id: str) -> Session:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    return enrich_session(session)


@app.get("/api/sessions/{session_id}/events")
async def session_events_sse(session_id: str) -> StreamingResponse:
    """Server-sent events for pipeline progress (observe → measure → …)."""
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")

    async def generate():
        queue = subscribe(session_id)
        try:
            status = session.status.value if hasattr(session.status, "value") else str(session.status)
            yield format_sse(
                "snapshot",
                {
                    "session_id": session_id,
                    "status": status,
                    "pipeline_stages": list(PIPELINE_STAGES),
                },
            )
            for entry in session.events[-30:]:
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("event", "progress"))
                yield format_sse(name, entry)
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield format_sse(msg["event"], msg["data"])
        finally:
            unsubscribe(session_id, queue)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/sessions/{session_id}/observe", response_model=RunResponse)
async def observe_session(session_id: str) -> RunResponse:
    return await _run_stage(session_id, "observe")


@app.post("/api/sessions/{session_id}/measure", response_model=RunResponse)
async def measure_session(session_id: str) -> RunResponse:
    return await _run_stage(session_id, "measure")


@app.post("/api/sessions/{session_id}/hypothesize", response_model=RunResponse)
async def hypothesize_session(session_id: str) -> RunResponse:
    return await _run_stage(session_id, "hypothesize")


@app.post("/api/sessions/{session_id}/imagine", response_model=RunResponse)
async def imagine_session(session_id: str) -> RunResponse:
    return await _run_stage(session_id, "imagine")


@app.post("/api/sessions/{session_id}/experiment", response_model=RunResponse)
async def experiment_session(session_id: str) -> RunResponse:
    return await _run_stage(session_id, "experiment")


    return RunResponse(session=session)


class VoiceTurnBody(BaseModel):
    session_id: str | None = None
    transcript: str | None = None
    audio_base64: str | None = None


@app.post("/api/sessions/{session_id}/experiment/propose", response_model=RunResponse)
async def experiment_propose(session_id: str) -> RunResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if not session.hypotheses:
        raise HTTPException(422, detail="hypothesize must complete first")
    session.experiment = propose_experiment(session.hypotheses)
    session.events.append({"stage": "experiment", "message": session.experiment.instruction[:240]})
    store.put(session)
    return RunResponse(session=enrich_session(session))


@app.post("/api/sessions/{session_id}/experiment/result", response_model=RunResponse)
async def experiment_result(session_id: str, body: ExperimentResult) -> RunResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    if session.experiment is None:
        raise HTTPException(422, detail="call experiment/propose first")
    session.experiment_result = body
    msg = body.notes or "Experiment result recorded"
    if body.observed_period_ratio is not None:
        msg = f"Period ratio {body.observed_period_ratio:.2f}× — {msg}"
    session.events.append({"stage": "experiment", "message": msg[:240]})
    store.put(session)
    return RunResponse(session=enrich_session(session))


@app.post("/api/voice/turn")
async def post_voice_turn(body: VoiceTurnBody) -> dict:
    session = store.get(body.session_id) if body.session_id else None
    if body.session_id and not session:
        raise HTTPException(404, "session not found")
    out = await voice_turn(
        settings=settings,
        session=session,
        transcript=body.transcript,
        audio_base64=body.audio_base64,
    )
    if session:
        store.put(session)
    return out


@app.post("/api/sessions/{session_id}/accept", response_model=RunResponse)
async def accept_session(session_id: str) -> RunResponse:
    resp = await _run_stage(session_id, "accept")
    return RunResponse(session=enrich_session(resp.session))


@app.post("/api/sessions/{session_id}/run", response_model=RunResponse)
async def run_session(
    session_id: str,
    domain_hint: str | None = None,
    from_stage: str | None = Query(default=None, description="Resume from stage (e.g. measure)"),
) -> RunResponse:
    if not store.get(session_id):
        raise HTTPException(404, "session not found")
    if from_stage:
        if from_stage not in PIPELINE_STAGES:
            raise HTTPException(422, detail=f"unknown from_stage; use one of {list(PIPELINE_STAGES)}")
        try:
            session = await run_pipeline_from(session_id, from_stage, domain_hint=domain_hint)
        except StageGuardError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return RunResponse(session=enrich_session(session))
    session = await run_full_pipeline(session_id, domain_hint=domain_hint)
    return RunResponse(session=enrich_session(session))


@app.get("/api/library/laws")
def list_laws() -> dict:
    laws = []
    for sid in sorted(store.list_ids()):
        s = store.get(sid)
        if s and s.notebook:
            completed = sum(
                1 for e in s.events if isinstance(e, dict) and e.get("event") == "stage_completed"
            )
            laws.append(
                {
                    "session_id": sid,
                    "law_latex": s.notebook.law_latex,
                    "params": s.notebook.params,
                    "mode": s.mode,
                    "error_bars": s.notebook.error_bars,
                    "stages_completed": completed,
                    "time_to_law_index": completed,
                }
            )
    return {"laws": laws, "count": len(laws)}
