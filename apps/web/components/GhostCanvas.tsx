"use client";

import { useEffect, useRef } from "react";

type Pt = { x_m: number; y_m: number };

export function GhostCanvas({
  real,
  ghost,
}: {
  real?: Pt[];
  ghost?: Pt[];
}) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    const pts = ghost?.length ? ghost : real || [];
    if (!pts.length) {
      ctx.fillStyle = "rgba(155,181,168,0.7)";
      ctx.font = "14px IBM Plex Mono, monospace";
      ctx.fillText("Waiting for trajectories…", 24, 40);
      return;
    }

    const xs = pts.map((p) => p.x_m);
    const ys = pts.map((p) => p.y_m);
    const minX = Math.min(...xs, 0);
    const maxX = Math.max(...xs, 0);
    const minY = Math.min(...ys, -0.01);
    const maxY = Math.max(...ys, 0.01);
    const pad = 36;
    const sx = (x: number) => pad + ((x - minX) / (maxX - minX || 1)) * (w - pad * 2);
    const sy = (y: number) => pad + ((maxY - y) / (maxY - minY || 1)) * (h - pad * 2);

    // pivot
    ctx.strokeStyle = "rgba(61,255,181,0.35)";
    ctx.beginPath();
    ctx.moveTo(sx(0), sy(0));
    ctx.lineTo(sx(0), h - pad);
    ctx.stroke();

    const draw = (series: Pt[] | undefined, color: string, width: number, dashed = false) => {
      if (!series?.length) return;
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.setLineDash(dashed ? [6, 6] : []);
      ctx.beginPath();
      series.forEach((p, i) => {
        const x = sx(p.x_m);
        const y = sy(p.y_m);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      const last = series[series.length - 1];
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(sx(last.x_m), sy(last.y_m), 5, 0, Math.PI * 2);
      ctx.fill();
    };

    draw(real, "rgba(244,255,248,0.9)", 2.2);
    draw(ghost, "rgba(255,107,61,0.95)", 2.4, true);

    ctx.setLineDash([]);
    ctx.fillStyle = "rgba(155,181,168,0.85)";
    ctx.font = "12px IBM Plex Mono, monospace";
    ctx.fillText("white = measured · ember dashed = HYPATIA ghost", 16, h - 14);
  }, [real, ghost]);

  return <canvas ref={ref} className="ghost-canvas" />;
}
