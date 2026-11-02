"use client";

import { useState } from "react";
import { postVoiceTurn } from "@/lib/api";

type Props = { sessionId: string | null };

export function VoiceMic({ sessionId }: Props) {
  const [reply, setReply] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function askDefault() {
    setBusy(true);
    try {
      const out = await postVoiceTurn({
        sessionId: sessionId ?? undefined,
        transcript: "What experiment should we run next?",
      });
      setReply(out.reply);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="voice-panel">
      <button type="button" className="btn secondary" disabled={busy} onClick={() => void askDefault()}>
        {busy ? "Listening…" : "Voice turn (fixture)"}
      </button>
      {reply ? <p className="meta" style={{ marginTop: "0.5rem" }}>{reply}</p> : null}
    </div>
  );
}
