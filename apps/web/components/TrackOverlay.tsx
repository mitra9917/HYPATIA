"use client";

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

/** Normalized 0–1 SAM-style boxes for demo overlay (full decode in #51). */
export function TrackOverlay({ tracks }: Props) {
  const track = tracks?.[0];
  const frames = track?.mask_frames ?? [];
  const preview = frames.length > 12 ? frames.filter((_, i) => i % 3 === 0) : frames;

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
        className="stage"
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
          {preview.map((f) => (
            <rect
              key={`${f.frame_index}-${f.t_s}`}
              x={f.bbox_norm.x}
              y={f.bbox_norm.y}
              width={f.bbox_norm.w}
              height={f.bbox_norm.h}
              fill="none"
              stroke="rgba(255, 107, 61, 0.55)"
              strokeWidth={0.008}
            />
          ))}
        </svg>
        <span
          className="meta"
          style={{
            position: "absolute",
            bottom: 8,
            left: 8,
            background: "rgba(0,0,0,0.45)",
            padding: "2px 6px",
            borderRadius: 4,
          }}
        >
          SAM overlay preview ({preview.length} boxes)
        </span>
      </div>
    </div>
  );
}
