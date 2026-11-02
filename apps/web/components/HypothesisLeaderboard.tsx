"use client";

import { KatexMath } from "@/components/KatexMath";
import type { Hypothesis } from "@/lib/types";

type Props = { hypotheses: Hypothesis[] };

export function HypothesisLeaderboard({ hypotheses }: Props) {
  if (!hypotheses.length) {
    return <p className="meta">Run hypothesize to spawn the Glimmer / SciPy rival swarm.</p>;
  }

  const maxScore = Math.max(...hypotheses.map((h) => h.heldout_score), 0.01);

  return (
    <div className="leaderboard" role="table" aria-label="Rival theories by held-out score">
      {hypotheses.map((h) => (
        <div key={h.id} className="leaderboard__row" role="row">
          <div role="cell">
            <KatexMath latex={h.form_latex} />
            <div className="meta">{h.status}</div>
          </div>
          <div className="meta" role="cell">
            {h.heldout_score.toFixed(3)}
          </div>
          <div className={`leaderboard__bar${h.status === "eliminated" ? " is-eliminated" : ""}`} role="cell">
            <span style={{ width: `${(h.heldout_score / maxScore) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
