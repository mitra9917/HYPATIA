"""P1.5 calibration — pixel tracks → SI units (Playbook #20 / issue #14)."""

from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass

from .models import BBoxNorm, MaskFrame, Track, TrajectoryPoint

# ISO A4 (metres)
A4_WIDTH_M = 0.210
A4_HEIGHT_M = 0.297
# India ₹10 coin diameter (approx)
INR_10_COIN_DIAMETER_M = 0.027

DEFAULT_PIVOT_NORM = (0.5, 0.18)


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    metres_per_pixel: float
    method: str  # a4_sheet | coin | default_fixture
    reference_length_m: float
    reference_pixels: float


def bbox_centroid_norm(box: BBoxNorm) -> tuple[float, float]:
    return box.x + box.w / 2.0, box.y + box.h / 2.0


def calibrate_from_a4_bbox(box: BBoxNorm, *, frame_width: int, frame_height: int) -> CalibrationResult:
    """Use detected A4 sheet bbox — long edge → 297 mm, short → 210 mm."""
    w_px = box.w * frame_width
    h_px = box.h * frame_height
    if h_px >= w_px:
        ref_m, ref_px = A4_HEIGHT_M, h_px
        method = "a4_long_edge"
    else:
        ref_m, ref_px = A4_WIDTH_M, w_px
        method = "a4_short_edge"
    ref_px = max(ref_px, 1.0)
    return CalibrationResult(
        metres_per_pixel=ref_m / ref_px,
        method=method,
        reference_length_m=ref_m,
        reference_pixels=ref_px,
    )


def calibrate_from_coin_bbox(
    box: BBoxNorm,
    *,
    frame_width: int,
    frame_height: int,
    diameter_m: float = INR_10_COIN_DIAMETER_M,
) -> CalibrationResult:
    w_px = box.w * frame_width
    h_px = box.h * frame_height
    ref_px = max((w_px + h_px) / 2.0, 1.0)
    return CalibrationResult(
        metres_per_pixel=diameter_m / ref_px,
        method="coin_diameter",
        reference_length_m=diameter_m,
        reference_pixels=ref_px,
    )


def default_fixture_calibration(mpp: float = 0.0012) -> CalibrationResult:
    return CalibrationResult(
        metres_per_pixel=mpp,
        method="default_fixture",
        reference_length_m=A4_WIDTH_M,
        reference_pixels=A4_WIDTH_M / mpp,
    )


def fixture_a4_mask() -> MaskFrame:
    """Synthetic A4 sheet bbox for fixture calibration (desk pendulum demo)."""
    return MaskFrame(
        frame_index=0,
        t_s=0.0,
        bbox_norm=BBoxNorm(x=0.12, y=0.52, w=0.38, h=0.28),
        track_id=99,
    )


def pick_scale_calibration(
    scale_masks: list[MaskFrame],
    *,
    frame_width: int,
    frame_height: int,
    scale_prompt: str,
) -> CalibrationResult | None:
    if not scale_masks:
        return None
    # Use median-sized scale detection (stable vs outliers)
    box = scale_masks[len(scale_masks) // 2].bbox_norm
    prompt = scale_prompt.lower()
    if "coin" in prompt or "₹" in prompt:
        return calibrate_from_coin_bbox(box, frame_width=frame_width, frame_height=frame_height)
    if "a4" in prompt or "sheet" in prompt or "paper" in prompt:
        return calibrate_from_a4_bbox(box, frame_width=frame_width, frame_height=frame_height)
    return calibrate_from_a4_bbox(box, frame_width=frame_width, frame_height=frame_height)


def trajectory_from_bob_masks(
    masks: list[MaskFrame],
    *,
    metres_per_pixel: float,
    frame_width: int,
    frame_height: int,
    pivot_norm: tuple[float, float] = DEFAULT_PIVOT_NORM,
    fps: float = 30.0,
    length_m: float | None = None,
) -> list[TrajectoryPoint]:
    """Centroid track → pendulum angles + Cartesian SI coords (pivot at top-centre)."""
    if not masks:
        return []
    px_w, px_h = float(frame_width), float(frame_height)
    pivot_x = pivot_norm[0] * px_w
    pivot_y = pivot_norm[1] * px_h
    points: list[TrajectoryPoint] = []
    for mf in sorted(masks, key=lambda m: m.frame_index):
        cx_n, cy_n = bbox_centroid_norm(mf.bbox_norm)
        cx, cy = cx_n * px_w, cy_n * px_h
        dx_px = cx - pivot_x
        dy_px = cy - pivot_y
        dx_m = dx_px * metres_per_pixel
        dy_m = dy_px * metres_per_pixel
        angle = math.atan2(dx_m, -dy_m)
        L = length_m
        if L is None:
            L = math.hypot(dx_m, dy_m) or 0.45
        points.append(
            TrajectoryPoint(
                t=mf.t_s if mf.t_s else mf.frame_index / fps,
                x_m=dx_m,
                y_m=dy_m,
                angle_rad=angle,
                length_m=L,
            )
        )
    if points and length_m is None:
        avg_L = sum(math.hypot(p.x_m or 0, p.y_m or 0) for p in points) / len(points)
        for p in points:
            p.length_m = avg_L
    return points


def estimate_period_from_angles(points: list[TrajectoryPoint]) -> float | None:
    """Zero-crossing period estimate for sanity checks / tests."""
    samples = [(p.t, p.angle_rad) for p in points if p.angle_rad is not None]
    if len(samples) < 10:
        return None
    crossings: list[float] = []
    for i in range(1, len(samples)):
        a0, a1 = samples[i - 1][1], samples[i][1]
        if a0 == 0:
            continue
        if a0 * a1 < 0:
            t0, t1 = samples[i - 1][0], samples[i][0]
            frac = abs(a0) / (abs(a0) + abs(a1) + 1e-12)
            crossings.append(t0 + frac * (t1 - t0))
    if len(crossings) < 2:
        return None
    half = [crossings[i + 1] - crossings[i] for i in range(len(crossings) - 1)]
    return float(2 * sum(half) / len(half))


def trajectory_to_csv(points: list[TrajectoryPoint]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["t_s", "x_m", "y_m", "angle_rad", "length_m"])
    for p in points:
        writer.writerow(
            [
                f"{p.t:.6f}",
                "" if p.x_m is None else f"{p.x_m:.6f}",
                "" if p.y_m is None else f"{p.y_m:.6f}",
                "" if p.angle_rad is None else f"{p.angle_rad:.6f}",
                "" if p.length_m is None else f"{p.length_m:.6f}",
            ]
        )
    return buf.getvalue()


def apply_si_calibration(
    track: Track,
    *,
    frame_width: int,
    frame_height: int,
    scale_masks: list[MaskFrame] | None = None,
    scale_prompt: str = "A4 sheet",
    fallback_length_m: float = 0.45,
) -> Track:
    """Replace or refine track points using mask centroids + scale calibration."""
    cal = None
    if scale_masks:
        cal = pick_scale_calibration(
            scale_masks,
            frame_width=frame_width,
            frame_height=frame_height,
            scale_prompt=scale_prompt,
        )
    if cal is None:
        cal = default_fixture_calibration(track.metres_per_pixel)

    masks = track.mask_frames
    si_points: list[TrajectoryPoint] = []
    if len(masks) >= 3:
        si_points = trajectory_from_bob_masks(
            masks,
            metres_per_pixel=cal.metres_per_pixel,
            frame_width=frame_width,
            frame_height=frame_height,
            fps=track.fps,
            length_m=fallback_length_m,
        )

    if len(si_points) >= 3:
        points = si_points
    else:
        points = track.points

    csv_out = trajectory_to_csv(points) if points else None
    return track.model_copy(
        update={
            "points": points,
            "metres_per_pixel": cal.metres_per_pixel,
            "calibration_method": cal.method,
            "trajectory_csv": csv_out,
        }
    )
