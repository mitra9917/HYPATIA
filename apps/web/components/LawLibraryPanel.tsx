"use client";

import { useEffect, useState } from "react";
import { listLaws } from "@/lib/api";
import type { LawSummary } from "@/lib/types";

export function LawLibraryPanel() {
  const [laws, setLaws] = useState<LawSummary[]>([]);

  useEffect(() => {
    void listLaws()
      .then(setLaws)
      .catch(() => setLaws([]));
  }, []);

  const maxStages = Math.max(1, ...laws.map((l) => l.stages_completed ?? 1));

  return (
    <div className="panel" style={{ marginTop: "1rem" }}>
      <h2>Law library</h2>
      {laws.length === 0 ? (
        <p className="meta">Accept a law to populate the library — second sessions get a cached hint.</p>
      ) : (
        <>
          <p className="meta">Self-improvement: fewer pipeline stages on repeat domains (stretch metric).</p>
          <div className="law-chart" aria-hidden={laws.length === 0}>
            {laws.map((law, i) => (
              <div key={law.session_id} className="law-chart__row">
                <span className="meta">{law.session_id.slice(0, 8)}</span>
                <div
                  className="law-chart__bar"
                  style={{ width: `${((law.stages_completed ?? 1) / maxStages) * 100}%` }}
                  title={`${law.stages_completed ?? "?"} stages to accept`}
                />
              </div>
            ))}
          </div>
          <div className="cards" style={{ marginTop: "0.75rem" }}>
            {laws.map((law) => (
              <div key={law.session_id} className="card winner">
                <div className="latex">{law.law_latex}</div>
                <div className="meta">
                  g ≈ {law.params.g?.toFixed?.(2) ?? "—"} · mode {law.mode}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
