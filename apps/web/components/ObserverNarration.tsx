"use client";

/** Spark Observer plain-language beat beside the lab view (P2.10 / #59, Playbook #36). */

type Props = {
  narration: string;
  domain?: string;
  /** Shown when observe stage has not run yet */
  placeholder?: string;
};

export function ObserverNarration({ narration, domain, placeholder }: Props) {
  const text = narration.trim() || placeholder || "Observer will narrate what the camera sees after the watch step.";
  return (
    <aside className="observer-narration" aria-live="polite" aria-label="Observer narration">
      <div className="observer-narration__label">
        <span className="pill">Muse Spark · Observer</span>
        {domain ? <span className="meta">{domain}</span> : null}
      </div>
      <p className="observer-narration__text">{text}</p>
    </aside>
  );
}
