"use client";

import type { Session } from "@/lib/types";

type Props = { session: Session | null };

export function AcceptGatePanel({ session }: Props) {
  const gate = session?.law_gate;
  if (!session?.hypotheses?.length) {
    return (
      <p className="meta">Held-out rivalry and bootstrap checks appear after hypothesize completes.</p>
    );
  }

  const rows = [
    { key: "held_out_winner", label: "Winner beats rivals on held-out R²", ok: gate?.held_out_winner },
    { key: "g_in_range", label: "g within demo bounds (~9.81 m/s²)", ok: gate?.g_in_range },
    {
      key: "bootstrap",
      label: "Bootstrap CI for g is sane",
      ok: gate?.bootstrap_ok ?? (gate?.reasons?.every((r) => !r.includes("bootstrap")) && gate?.ok),
    },
  ];

  return (
    <div>
      <p className="meta" style={{ marginBottom: "0.5rem" }}>
        LLM proposes · maths decides — accept only when all gates pass.
      </p>
      <ul className="gate-list">
        {rows.map((r) => (
          <li key={r.key} className={r.ok ? "is-ok" : undefined}>
            {r.label}
          </li>
        ))}
      </ul>
      {gate?.reasons?.length && !gate.ok ? (
        <p className="meta" style={{ marginTop: "0.75rem" }}>
          {gate.reasons.join(" · ")}
        </p>
      ) : null}
      {gate?.ok ? (
        <p style={{ marginTop: "0.75rem", color: "var(--success)", fontSize: "0.9rem" }}>
          Ready to commit law
        </p>
      ) : null}
    </div>
  );
}
