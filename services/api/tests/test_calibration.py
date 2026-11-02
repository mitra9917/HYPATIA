"""P1.5 calibration tests (Playbook #20 / #14) — no Meta."""

from __future__ import annotations

import pytest

from hypatia.calibration import (
    A4_HEIGHT_M,
    calibrate_from_a4_bbox,
    calibrate_from_coin_bbox,
    default_fixture_calibration,
    estimate_period_from_angles,
    fixture_a4_mask,
    trajectory_from_bob_masks,
    trajectory_to_csv,
)
from hypatia.models import BBoxNorm


def test_a4_calibration_portrait_sheet() -> None:
    # Taller than wide in pixel space → long edge 297 mm
    box = BBoxNorm(x=0.2, y=0.4, w=0.15, h=0.35)
    cal = calibrate_from_a4_bbox(box, frame_width=1280, frame_height=720)
    assert cal.method == "a4_long_edge"
    expected_mpp = A4_HEIGHT_M / (0.35 * 720)
    assert cal.metres_per_pixel == pytest.approx(expected_mpp, rel=0.01)


def test_coin_calibration() -> None:
    box = BBoxNorm(x=0.4, y=0.4, w=0.02, h=0.02)
    cal = calibrate_from_coin_bbox(box, frame_width=1000, frame_height=1000)
    assert cal.method == "coin_diameter"
    assert cal.metres_per_pixel > 0


def test_trajectory_from_masks_has_angles_and_csv() -> None:
    from hypatia.models import MaskFrame

    masks = [
        MaskFrame(
            frame_index=i,
            t_s=i / 30.0,
            bbox_norm=BBoxNorm(x=0.48 + i * 0.002, y=0.35, w=0.04, h=0.04),
            track_id=1,
        )
        for i in range(20)
    ]
    mpp = default_fixture_calibration().metres_per_pixel
    pts = trajectory_from_bob_masks(
        masks,
        metres_per_pixel=mpp,
        frame_width=1280,
        frame_height=720,
        fps=30.0,
    )
    assert len(pts) == 20
    assert all(p.angle_rad is not None for p in pts)
    csv = trajectory_to_csv(pts)
    assert csv.startswith("t_s,x_m,y_m,angle_rad,length_m")
    period = estimate_period_from_angles(pts)
    assert period is None or period > 0


def test_fixture_a4_mask_calibrates() -> None:
    m = fixture_a4_mask()
    cal = calibrate_from_a4_bbox(m.bbox_norm, frame_width=1280, frame_height=720)
    assert cal.metres_per_pixel > 0
