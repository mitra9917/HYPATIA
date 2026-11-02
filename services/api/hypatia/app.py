from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .glimmer import run_glimmer_swarm
from .meta_client import MetaClient
from .models import CreateSessionResponse, RunResponse, Session
from .observer import run_observer
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


@app.get("/api/sessions/{session_id}", response_model=Session)
def get_session(session_id: str) -> Session:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    return session


@app.post("/api/sessions/{session_id}/observe", response_model=RunResponse)
async def observe_session(session_id: str) -> RunResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(404, "session not found")
    session = await run_observer(session)
    return RunResponse(session=session)


@app.post("/api/sessions/{session_id}/run", response_model=RunResponse)
async def run_session(session_id: str, domain_hint: str | None = None) -> RunResponse:
    if not store.get(session_id):
        raise HTTPException(404, "session not found")
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
