"use client";

import { useMemo, useState } from "react";

type BBox = { x: number; y: number; w: number; h: number };

type MaskFrame = {
  frame_index: number;
  t_s: number;
  bbox_norm: BBox;
  track_id?: number;
};

type Track = {
  object_name: string;
  sam_prompt: string;
  points: { t: number; x_m?: number; y_m?: number; angle_rad?: number }[];
  mask_frames: MaskFrame[];
  source: string;
  frame_cost?: {
    frames_billed_estimate: number;
    scientific_fps: number;
  } | null;
};

type Props = {
  tracks: Track[] | undefined;
};

/** SAM mask boxes with frame scrubber (P1.7 / #16). */
export function TrackOverlay({ tracks }: Props) {
  const track = tracks?.[0];
  const frames = useMemo(() => track?.mask_frames ?? [], [track?.mask_frames]);
  const [frameIdx, setFrameIdx] = useState(0);

  const active = useMemo(() => {
    if (!frames.length) return null;
    const i = Math.min(Math.max(frameIdx, 0), frames.length - 1);
    return frames[i];
  }, [frames, frameIdx]);

  if (!track) {
    return <p className="meta">Measurer will attach mask frames after measure.</p>;
  }

  return (
    <div>
      <p className="meta">
        {track.object_name} · source={track.source} · {track.points.length} trajectory samples ·{" "}
        {frames.length} mask frames
        {track.frame_cost
          ? ` · ~${track.frame_cost.frames_billed_estimate} frames @ ${track.frame_cost.scientific_fps} fps`
          : null}
      </p>
      <div
        className="stage track-overlay-stage"
        style={{
          marginTop: "0.75rem",
          aspectRatio: "16 / 10",
          background: "linear-gradient(180deg, #0a1220 0%, #121c2e 100%)",
          position: "relative",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      >
        <svg viewBox="0 0 1 1" preserveAspectRatio="none" style={{ width: "100%", height: "100%" }}>
          {frames.map((f) => (
            <rect
              key={`ghost-${f.frame_index}-${f.t_s}`}
              x={f.bbox_norm.x}
              y={f.bbox_norm.y}
              width={f.bbox_norm.w}
              height={f.bbox_norm.h}
              fill="none"
              stroke="rgba(61, 255, 181, 0.12)"
              strokeWidth={0.006}
            />
          ))}
          {active ? (
            <rect
              x={active.bbox_norm.x}
              y={active.bbox_norm.y}
              width={active.bbox_norm.w}
              height={active.bbox_norm.h}
              fill="rgba(255, 107, 61, 0.15)"
              stroke="rgba(255, 107, 61, 0.9)"
              strokeWidth={0.012}
            />
          ) : null}
        </svg>
        <span className="overlay-caption meta">
          {active
            ? `frame ${active.frame_index} · t=${active.t_s.toFixed(2)}s`
            : "No mask frames"}
        </span>
      </div>
      {frames.length > 1 ? (
        <label className="meta frame-scrubber">
          Scrub masks
          <input
            type="range"
            min={0}
            max={frames.length - 1}
            value={Math.min(frameIdx, frames.length - 1)}
            onChange={(e) => setFrameIdx(Number(e.target.value))}
          />
        </label>
      ) : null}
    </div>
  );
}
