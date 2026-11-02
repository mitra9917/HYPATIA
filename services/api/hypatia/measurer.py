"""P1.4 SAM 3.1 measurer — tracks, mask summaries, fixture cache (Playbook #18 / #13)."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from .config import FIXTURE_DIR, Settings, get_settings
from .meta_client import MetaClient
from .meta_files import primary_video_file_id
from .media_utils import session_media_size
from .models import (
    BBoxNorm,
    FrameCostEstimate,
    MaskFrame,
    Session,
    SessionStatus,
    Track,
    TrajectoryPoint,
)
from .sam_decode import parse_sam_response
from .science import synthesize_pendulum_track
from .store import store

TRACK_FIXTURE_DIR = FIXTURE_DIR / "tracks"
DEFAULT_LENGTH_M = 0.45
DEFAULT_CLIP_S = 4.0
DEFAULT_SOURCE_FPS = 30.0
SCIENTIFIC_FPS = 12.5  # 10–15 fps guard per META_TOOLING.md


def _slug(prompt: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", prompt.lower().strip()).strip("_") or "object"


def _event(session: Session, message: str) -> None:
    session.events.append({"stage": "measure", "message": message})


def estimate_frame_cost(
    *,
    clip_duration_s: float = DEFAULT_CLIP_S,
    source_fps: float = DEFAULT_SOURCE_FPS,
    scientific_fps: float = SCIENTIFIC_FPS,
) -> FrameCostEstimate:
    """Downsampled frame count billed for SAM-style video calls."""
    source_frames = max(1, int(round(clip_duration_s * source_fps)))
    billed = max(1, int(round(clip_duration_s * scientific_fps)))
    billed = min(billed, source_frames)
    return FrameCostEstimate(
        source_fps=source_fps,
        scientific_fps=scientific_fps,
        clip_duration_s=clip_duration_s,
        frames_billed_estimate=billed,
    )


def trajectory_to_mask_frames(
    points: list[TrajectoryPoint],
    *,
    length_m: float,
    every_n: int = 3,
) -> list[MaskFrame]:
    """Geometric proxy boxes for UI overlay when SAM masks are unavailable."""
    if not points:
        return []
    span = max(length_m * 2.2, 0.2)
    box = 0.06
    frames: list[MaskFrame] = []
    for i, p in enumerate(points):
        if i % every_n != 0 and i != len(points) - 1:
            continue
        x_m = p.x_m if p.x_m is not None else 0.0
        y_m = p.y_m if p.y_m is not None else -length_m
        cx = 0.5 + x_m / span
        cy = 0.42 + y_m / span
        cx = min(max(cx - box / 2, 0.0), 1.0 - box)
        cy = min(max(cy - box / 2, 0.0), 1.0 - box)
        frames.append(
            MaskFrame(
                frame_index=i,
                t_s=p.t,
                bbox_norm=BBoxNorm(x=cx, y=cy, w=box, h=box),
                track_id=0,
            )
        )
    return frames


def _cache_path(session_id: str, prompt: str) -> Path:
    TRACK_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    return TRACK_FIXTURE_DIR / f"{session_id}_{_slug(prompt)}.json"


def _default_fixture_path(prompt: str) -> Path:
    slug = _slug(prompt)
    if "bob" in slug or slug == "pendulum_bob":
        return TRACK_FIXTURE_DIR / "pendulum_bob_default.json"
    return TRACK_FIXTURE_DIR / f"{slug}_default.json"


def load_cached_track(session_id: str, prompt: str) -> Track | None:
    for path in (_cache_path(session_id, prompt), _default_fixture_path(prompt)):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
            return Track.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            continue
    return None


def save_cached_track(session_id: str, prompt: str, track: Track) -> Path:
    path = _cache_path(session_id, prompt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(track.model_dump_json(indent=2))
    return path


def _object_name_for_prompt(prompt: str) -> str:
    return prompt.strip() or "tracked object"


def _build_fixture_track(
    *,
    prompt: str,
    length_m: float,
    frame_cost: FrameCostEstimate,
    source: str,
) -> Track:
    points = synthesize_pendulum_track(length_m=length_m, duration_s=frame_cost.clip_duration_s, fps=frame_cost.source_fps)
    masks = trajectory_to_mask_frames(points, length_m=length_m)
    return Track(
        object_name=_object_name_for_prompt(prompt),
        sam_prompt=prompt,
        points=points,
        mask_frames=masks,
        metres_per_pixel=0.0012,
        fps=frame_cost.source_fps,
        source=source,
        frame_cost=frame_cost,
    )


def _log_frame_cost(session: Session, settings: Settings, frame_cost: FrameCostEstimate) -> None:
    session.meta_calls.append(
        {
            "model": settings.meta_sam_model,
            "kind": "measurer.frame_cost",
            "ok": True,
            "scientific_fps": frame_cost.scientific_fps,
            "source_fps": frame_cost.source_fps,
            "clip_duration_s": frame_cost.clip_duration_s,
            "frames_billed_estimate": frame_cost.frames_billed_estimate,
            "session_id": session.id,
        }
    )


async def run_measurer(session: Session, client: MetaClient, settings: Settings | None = None) -> Session:
    """Run SAM 3.1 measure stage: tracks + mask summaries with fixture/hybrid fallback."""
    settings = settings or get_settings()
    session.status = SessionStatus.measuring
    _event(session, "SAM 3.1 tracking → metres (fixture cache + live when available)")

    prompts = list(session.scene.sam_prompts if session.scene else []) or ["pendulum bob"]
    primary_prompt = prompts[0]
    frame_cost = estimate_frame_cost()
    _log_frame_cost(session, settings, frame_cost)
    _event(
        session,
        f"Frame cost estimate: ~{frame_cost.frames_billed_estimate} frames @ "
        f"{frame_cost.scientific_fps} fps (from {frame_cost.source_fps} fps clip)",
    )

    length_m = DEFAULT_LENGTH_M
    track: Track | None = None
    source = "fixture"

    if settings.effective_fixture_mode:
        track = load_cached_track(session.id, primary_prompt)
        if track is None:
            track = _build_fixture_track(
                prompt=primary_prompt,
                length_m=length_m,
                frame_cost=frame_cost,
                source="fixture",
            )
        else:
            track.frame_cost = frame_cost
            if not track.mask_frames and track.points:
                track.mask_frames = trajectory_to_mask_frames(track.points, length_m=length_m)
        _event(session, f"Fixture track loaded for «{primary_prompt}» ({len(track.points)} samples)")

    elif client.enabled and session.mode == "live":
        file_id = primary_video_file_id(session)
        media_size = session_media_size(session)
        sam_masks: list[MaskFrame] = []
        started = time.time()
        try:
            if file_id:
                sam_masks, log = await client.segment_video_tracked(
                    primary_prompt,
                    file_id=file_id,
                    media_size=media_size,
                )
                log["latency_ms"] = int((time.time() - started) * 1000)
            else:
                raw, log = client.segment_video_stub_prompt(primary_prompt, file_id=file_id)
                log["latency_ms"] = int((time.time() - started) * 1000)
                sam_masks = parse_sam_response(
                    raw,
                    width=media_size[0],
                    height=media_size[1],
                )
            session.meta_calls.append(log)
            source = "sam" if sam_masks else "hybrid"
            _event(
                session,
                f"SAM decoded {len(sam_masks)} mask frames (meta_sam_parser)"
                if sam_masks
                else "SAM returned no decodable masks — calibrated synthesis (hybrid)",
            )
        except Exception as exc:  # noqa: BLE001
            session.meta_calls.append(
                {
                    "model": settings.meta_sam_model,
                    "kind": "sam",
                    "ok": False,
                    "error": str(exc)[:200],
                    "file_id": file_id,
                }
            )
            session.mode = "hybrid"
            source = "hybrid"
            _event(session, f"SAM unavailable ({exc}); using calibrated fixture track")

        track = _build_fixture_track(
            prompt=primary_prompt,
            length_m=length_m,
            frame_cost=frame_cost,
            source=source,
        )
        if sam_masks:
            track.mask_frames = sam_masks
        save_cached_track(session.id, primary_prompt, track)

    else:
        track = _build_fixture_track(
            prompt=primary_prompt,
            length_m=length_m,
            frame_cost=frame_cost,
            source="fixture",
        )

    session.tracks = [track]
    if settings.effective_fixture_mode or session.mode in {"fixture", "hybrid"}:
        save_cached_track(session.id, primary_prompt, track)

    _event(
        session,
        f"Trajectory ready: {len(track.points)} samples, {len(track.mask_frames)} mask frames, "
        f"L≈{length_m} m, source={track.source}",
    )
    store.put(session)
    return session
