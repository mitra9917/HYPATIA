"use client";

import { KatexMath } from "@/components/KatexMath";
import type { Hypothesis } from "@/lib/types";

type Props = { hypothesis: Hypothesis; demoLine?: string };

export function HypothesisCard({ hypothesis: h, demoLine }: Props) {
  return (
    <div className={`card ${h.status}`}>
      <div className="latex">
        <KatexMath latex={h.form_latex} display />
      </div>
      <div className="meta">{h.form_plain}</div>
      <div className="meta">
        train R² {h.train_score.toFixed(3)} · held-out {h.heldout_score.toFixed(3)} ·{" "}
        <strong>{h.status}</strong>
      </div>
      {h.param_ci?.g ? (
        <div className="meta">
          g CI [{h.param_ci.g[0].toFixed(2)}, {h.param_ci.g[1].toFixed(2)}] m/s²
        </div>
      ) : null}
      {demoLine && h.status === "winner" ? (
        <p style={{ marginTop: "0.5rem", fontSize: "0.92rem" }}>{demoLine}</p>
      ) : null}
    </div>
  );
}
