"use client";

import { useState } from "react";
import { setOpsMode, type OpsMode } from "@/lib/api";

type Props = {
  ops?: {
    ops_mode?: string;
    ops_mode_override?: string | null;
    fixture_mode?: boolean;
    hybrid_fallback_enabled?: boolean;
    locked?: boolean;
  };
  onModeChange?: () => void;
};

export function OpsModeBanner({ ops, onModeChange }: Props) {
  const [busy, setBusy] = useState(false);
  const mode = ops?.ops_mode ?? "fixture";

  async function flip(next: OpsMode) {
    setBusy(true);
    try {
      await setOpsMode(next);
      onModeChange?.();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="contributor-banner shell" role="status">
      <strong>Ops mode</strong>
      <span className="meta">
        {mode}
        {ops?.hybrid_fallback_enabled ? " · hybrid fallback on" : ""}
        {ops?.fixture_mode ? " · replay/fixtures active" : " · live Meta paths"}
      </span>
      <span style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
        {(["fixture", "live", "hybrid"] as OpsMode[]).map((m) => (
          <button
            key={m}
            type="button"
            className={`btn secondary${mode === m ? " winner" : ""}`}
            disabled={busy || mode === m || Boolean(ops?.locked)}
            title={ops?.locked ? "Mode is locked on this public deployment" : undefined}
            onClick={() => void flip(m)}
          >
            {m}
          </button>
        ))}
      </span>
    </div>
  );
}
