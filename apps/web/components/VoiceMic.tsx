"use client";

import { useState } from "react";
import { postVoiceTurn, voiceRealtimeUrl } from "@/lib/api";

type Props = { sessionId: string | null };

export function VoiceMic({ sessionId }: Props) {
  const [reply, setReply] = useState<string | null>(null);
  const [partial, setPartial] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function askFixture() {
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

  async function askRealtime() {
    if (typeof WebSocket === "undefined") {
      return askFixture();
    }
    setBusy(true);
    setPartial(null);
    setReply(null);
    try {
      await new Promise<void>((resolve, reject) => {
        const ws = new WebSocket(voiceRealtimeUrl(sessionId ?? undefined));
        ws.onopen = () => {
          ws.send(JSON.stringify({ type: "commit", transcript: "What experiment should we run next?" }));
        };
        ws.onmessage = (ev) => {
          const data = JSON.parse(String(ev.data)) as { type: string; transcript?: string; text?: string };
          if (data.type === "partial" && data.transcript) setPartial(data.transcript);
          if (data.type === "final" && data.transcript) setPartial(data.transcript);
          if (data.type === "reply" && data.text) {
            setReply(data.text);
            ws.close();
            resolve();
          }
        };
        ws.onerror = () => reject(new Error("WebSocket failed"));
        ws.onclose = () => resolve();
      });
    } catch {
      await askFixture();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="voice-panel">
      <button type="button" className="btn secondary" disabled={busy} onClick={() => void askRealtime()}>
        {busy ? "Listening…" : "Voice (WebSocket → fallback)"}
      </button>
      {partial ? <p className="meta" style={{ marginTop: "0.35rem" }}>{partial}</p> : null}
      {reply ? <p className="meta" style={{ marginTop: "0.5rem" }}>{reply}</p> : null}
    </div>
  );
}
