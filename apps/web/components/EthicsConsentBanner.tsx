"use client";

type Props = {
  checked: boolean;
  onChange: (value: boolean) => void;
};

export function EthicsConsentBanner({ checked, onChange }: Props) {
  return (
    <div className="fixture-banner shell" role="group" aria-labelledby="ethics-consent-label">
      <label id="ethics-consent-label" style={{ display: "flex", gap: "0.5rem", alignItems: "flex-start" }}>
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          style={{ marginTop: "0.2rem" }}
        />
        <span>
          I confirm this clip is safe for a <strong>public demo</strong> — no sensitive lab IP, faces, or
          classified content. HYPATIA stores session metadata only for science replay.
        </span>
      </label>
    </div>
  );
}
