"""M3 ghost pipeline tests — Playbook #31–33 / issues #26–#28."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("FIXTURE_MODE", "true")

from hypatia.imagination_audit import bbox_iou, sam_imagination_audit
from hypatia.models import BBoxNorm, Hypothesis
from hypatia.predictor import forward_polyline, initial_state, state_at_delta
from hypatia.science import G, synthesize_pendulum_track


def _winner() -> Hypothesis:
    return Hypothesis(
        id="w1",
        form_latex=r"T = 2\pi\sqrt{L/g}",
        form_plain="pendulum",
        params={"g": G, "L": 0.45},
        heldout_score=0.9,
        status="winner",
    )


def test_forward_polyline_near_ground_truth() -> None:
    import math

    points = synthesize_pendulum_track(length_m=0.45, g=G, noise=0.0, duration_s=2.0)
    hyp = _winner()
    ghost = forward_polyline(points, hyp, steps=30, fps=30.0)
    assert len(ghost) == 30
    t0 = points[-1].t + 0.5
    omega = math.sqrt(G / 0.45)
    amp = 0.35
    truth_x = 0.45 * math.sin(amp * math.cos(omega * t0))
    pred = min(ghost, key=lambda g: abs(g["t"] - t0))
    assert abs(truth_x - pred["x_m"]) < 0.06


def test_state_at_delta_returns_point() -> None:
    points = synthesize_pendulum_track(noise=0.0)
    delta = state_at_delta(points, _winner(), 0.25)
    assert "x_m" in delta and "angle_rad" in delta


def test_bbox_iou_identical() -> None:
    b = BBoxNorm(x=0.4, y=0.4, w=0.1, h=0.1)
    assert bbox_iou(b, b) == pytest.approx(1.0)


def test_sam_audit_returns_iou_and_centroid() -> None:
    from hypatia.imagination_audit import metre_xy_to_bbox_norm
    from hypatia.models import MaskFrame, Track

    points = synthesize_pendulum_track(length_m=0.45, noise=0.0)
    masks = [
        MaskFrame(
            frame_index=i,
            t_s=p.t,
            bbox_norm=metre_xy_to_bbox_norm(p.x_m or 0, p.y_m or 0, length_m=0.45),
        )
        for i, p in enumerate(points[::4])
    ]
    track = Track(object_name="bob", sam_prompt="bob", points=points, mask_frames=masks)
    ghost = forward_polyline(points, _winner(), steps=20)
    audit = sam_imagination_audit(track, points, ghost)
    assert 0.0 <= audit["audit_iou"] <= 1.0
    assert audit["audit_centroid_m"] >= 0.0
