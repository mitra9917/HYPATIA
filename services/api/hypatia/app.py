from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .config import get_settings
from .glimmer import run_glimmer_swarm
from .meta_client import MetaClient
from .models import CreateSessionResponse, RunResponse, Session
from .orchestrator import PIPELINE_STAGES, StageGuardError, run_pipeline_from, run_pipeline_stage
from .pipeline import create_session, run_full_pipeline
from .store import store

settings = get_settings()

app = FastAPI(
    title="HYPATIA API",
    description="The camera that does science — Meta Model API + partner open weights",
    version="0.1.0",
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
    return RunResponse(session=session)


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
    return {
        "ok": True,
        "service": "hypatia-api",
        "fixture_mode": settings.effective_fixture_mode,
        "model_router": settings.model_router(),
        "pipeline_stages": list(PIPELINE_STAGES),
        "glimmer_provider": settings.glimmer_provider,
        "glimmer": glimmer_probe,
        "meta": client.health_ping() if settings.has_meta_key else {"meta": False, "reason": "no key"},
        "s3_configured": bool(settings.s3_bucket and settings.aws_access_key_id),
        "database_configured": bool(settings.database_url.strip()),
        "session_store": "memory",
        "deploy_priority": ["meta_model_api", "modal", "baseten", "fireworks", "aws"],
    }


@app.post("/api/sessions", response_model=CreateSessionResponse)
async def post_session(file: UploadFile | None = File(default=None)) -> CreateSessionResponse:
    raw = await file.read() if file is not None else None
    filename = file.filename if file is not None else "webcam-or-fixture"
    source = "upload" if file is not None else "fixture"
    session = await create_session(filename=filename, source_type=source, raw=raw)
    return CreateSessionResponse(session=session)


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
    return session


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


@app.post("/api/sessions/{session_id}/accept", response_model=RunResponse)
async def accept_session(session_id: str) -> RunResponse:
    return await _run_stage(session_id, "accept")


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
        return RunResponse(session=session)
    session = await run_full_pipeline(session_id, domain_hint=domain_hint)
    return RunResponse(session=session)


@app.get("/api/library/laws")
def list_laws() -> dict:
    laws = []
    for sid in store.list_ids():
        s = store.get(sid)
        if s and s.notebook:
            laws.append(
                {
                    "session_id": sid,
                    "law_latex": s.notebook.law_latex,
                    "params": s.notebook.params,
                    "mode": s.mode,
                }
            )
    return {"laws": laws}
