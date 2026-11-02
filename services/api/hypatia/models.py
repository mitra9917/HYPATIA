from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    created = "created"
    observing = "observing"
    measuring = "measuring"
    hypothesizing = "hypothesizing"
    imagining = "imagining"
    experimenting = "experimenting"
    accepted = "accepted"
    failed = "failed"


class SceneObject(BaseModel):
    name: str
    why_interesting: str = ""


class SceneBrief(BaseModel):
    objects: list[SceneObject] = Field(default_factory=list)
    candidate_variables: list[str] = Field(default_factory=list)
    sam_prompts: list[str] = Field(default_factory=list)
    suggested_domain: str = "mechanics.unknown"
    narration: str = ""


class TrajectoryPoint(BaseModel):
    t: float
    x_m: float | None = None
    y_m: float | None = None
    angle_rad: float | None = None
    length_m: float | None = None


class Track(BaseModel):
    object_name: str
    sam_prompt: str
    points: list[TrajectoryPoint] = Field(default_factory=list)
    metres_per_pixel: float = 0.001
    fps: float = 30.0


class Hypothesis(BaseModel):
    id: str
    form_latex: str
    form_plain: str
    params: dict[str, float] = Field(default_factory=dict)
    train_score: float = 0.0
    heldout_score: float = 0.0
    r2_heldout: float = 0.0
    status: str = "candidate"  # candidate | eliminated | winner


class ExperimentProposal(BaseModel):
    instruction: str
    rationale: str
    expected_outcomes: dict[str, str] = Field(default_factory=dict)


class ImaginationFrame(BaseModel):
    hypothesis_id: str
    predicted_description: str
    audit_error_m: float
    ghost_polyline: list[dict[str, float]] = Field(default_factory=list)
    source: str = "geometric"  # muse_image | geometric | fixture


class Notebook(BaseModel):
    markdown: str
    law_latex: str
    params: dict[str, float] = Field(default_factory=dict)
    error_bars: dict[str, float] = Field(default_factory=dict)


class Session(BaseModel):
    id: str
    status: SessionStatus = SessionStatus.created
    source_type: str = "upload"
    filename: str | None = None
    mode: str = "fixture"  # live | hybrid | fixture
    domain_hint: str | None = None
    video_file_id: str | None = None
    meta_file_ids: list[str] = Field(default_factory=list)
    scene: SceneBrief | None = None
    tracks: list[Track] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    experiment: ExperimentProposal | None = None
    imagination: list[ImaginationFrame] = Field(default_factory=list)
    notebook: Notebook | None = None
    events: list[dict[str, Any]] = Field(default_factory=list)
    meta_calls: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class CreateSessionResponse(BaseModel):
    session: Session


class RunResponse(BaseModel):
    session: Session
