"""SAM-style imagination audit — IoU + centroid (P3.3 / Playbook #33, issue #28)."""

from __future__ import annotations

import math

from .models import BBoxNorm, MaskFrame, Track, TrajectoryPoint


def bbox_iou(a: BBoxNorm, b: BBoxNorm) -> float:
    ax2, ay2 = a.x + a.w, a.y + a.h
    bx2, by2 = b.x + b.w, b.y + b.h
    ix1, iy1 = max(a.x, b.x), max(a.y, b.y)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = a.w * a.h + b.w * b.h - inter
    return float(inter / max(union, 1e-12))


def metre_xy_to_bbox_norm(x_m: float, y_m: float, *, length_m: float, box: float = 0.06) -> BBoxNorm:
    """Same projection as measurer.trajectory_to_mask_frames."""
    span = max(length_m * 2.2, 0.2)
    cx = 0.5 + x_m / span
    cy = 0.42 + y_m / span
    cx = min(max(cx - box / 2, 0.0), 1.0 - box)
    cy = min(max(cy - box / 2, 0.0), 1.0 - box)
    return BBoxNorm(x=cx, y=cy, w=box, h=box)


def _mask_at_time(frames: list[MaskFrame], t_s: float) -> MaskFrame | None:
    if not frames:
        return None
    return min(frames, key=lambda f: abs(f.t_s - t_s))


def sam_imagination_audit(
    track: Track | None,
    points: list[TrajectoryPoint],
    ghost: list[dict[str, float]],
    *,
    horizon_s: float = 0.5,
) -> dict[str, float]:
    """Compare predicted vs real at t+Δ; SAM grades Muse Image proxy via mask IoU."""
    if not points or not ghost:
        return {"audit_error_m": 0.05, "audit_iou": 0.0, "audit_centroid_m": 0.05}

    last = points[-1]
    t_target = last.t + horizon_s
    ghost_pt = min(ghost, key=lambda g: abs(float(g["t"]) - t_target))
    gx = float(ghost_pt.get("x_m") or 0.0)
    gy = float(ghost_pt.get("y_m") or 0.0)
    length = float(last.length_m or track.metres_per_pixel * 400 if track else 0.45)

    real_future = min(points, key=lambda p: abs(p.t - t_target))
    rx = float(real_future.x_m or 0.0)
    ry = float(real_future.y_m or 0.0)
    centroid_m = math.hypot(rx - gx, ry - gy)

    iou = 0.0
    if track and track.mask_frames:
        real_mask = _mask_at_time(track.mask_frames, t_target)
        if real_mask:
            pred_box = metre_xy_to_bbox_norm(gx, gy, length_m=length)
            iou = bbox_iou(real_mask.bbox_norm, pred_box)

    trail_err = 0.0
    n = min(20, len(points), len(ghost))
    if n:
        errs = []
        for i in range(n):
            p = points[-(n - i)]
            g = ghost[i]
            errs.append(
                math.hypot((p.x_m or 0) - g["x_m"], (p.y_m or 0) - g["y_m"])
            )
        trail_err = float(sum(errs) / len(errs))

    audit_m = max(centroid_m, trail_err * 0.35)
    return {
        "audit_error_m": round(audit_m, 4),
        "audit_iou": round(iou, 4),
        "audit_centroid_m": round(centroid_m, 4),
    }
