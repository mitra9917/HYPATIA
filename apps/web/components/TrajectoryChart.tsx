"use client";

import { useMemo } from "react";

type Point = {
  t: number;
  x_m?: number;
  y_m?: number;
  angle_rad?: number;
};

type Props = {
  points: Point[] | undefined;
  title?: string;
};

const W = 320;
const H = 140;
const PAD = 28;

/** Pendulum-friendly chart: angle (deg) vs time. */
export function TrajectoryChart({ points, title = "Trajectory" }: Props) {
  const series = useMemo(() => {
    const pts = (points ?? []).filter((p) => p.angle_rad != null);
    if (!pts.length) return null;
    const tMin = pts[0].t;
    const tMax = pts[pts.length - 1].t;
    const angles = pts.map((p) => ((p.angle_rad as number) * 180) / Math.PI);
    const aMin = Math.min(...angles);
    const aMax = Math.max(...angles);
    const tSpan = Math.max(tMax - tMin, 0.001);
    const aSpan = Math.max(aMax - aMin, 0.01);
    const path = pts
      .map((p, i) => {
        const x = PAD + ((p.t - tMin) / tSpan) * (W - PAD * 2);
        const y = H - PAD - (((p.angle_rad as number) * 180) / Math.PI - aMin) / aSpan * (H - PAD * 2);
        return `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(" ");
    return { path, tMin, tMax, aMin, aMax, n: pts.length };
  }, [points]);

  if (!series) {
    return <p className="meta">Trajectory chart appears after measure (angle vs time).</p>;
  }

  return (
    <div className="trajectory-chart">
      <p className="meta">
        {title} · {series.n} samples · θ [{series.aMin.toFixed(1)}°, {series.aMax.toFixed(1)}°] · t [
        {series.tMin.toFixed(2)}, {series.tMax.toFixed(2)}] s
      </p>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Angle versus time chart">
        <rect x={0} y={0} width={W} height={H} fill="rgba(0,0,0,0.25)" rx={6} />
        <line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="var(--line)" strokeWidth={1} />
        <line x1={PAD} y1={PAD} x2={PAD} y2={H - PAD} stroke="var(--line)" strokeWidth={1} />
        <path d={series.path} fill="none" stroke="var(--signal)" strokeWidth={2} />
        <text x={PAD} y={14} fill="var(--fog-dim)" fontSize={10}>
          θ (deg)
        </text>
        <text x={W - PAD - 36} y={H - 8} fill="var(--fog-dim)" fontSize={10}>
          t (s)
        </text>
      </svg>
    </div>
  );
}
