"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { KatexMath } from "@/components/KatexMath";
import { PageHeader } from "@/components/shell/PageHeader";
import {
  cellsNotebookDownloadUrl,
  getSession,
  notebookDownloadUrl,
} from "@/lib/api";
import type { Session } from "@/lib/types";
import { getActiveSessionId, getRecentSessionIds } from "@/lib/recent-sessions";

export default function NotebookPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const active = getActiveSessionId();
    const recent = getRecentSessionIds();
    const id = active || recent[0] || null;
    setSessionId(id);
  }, []);

  useEffect(() => {
    if (!sessionId) return;
    void getSession(sessionId)
      .then((s) => {
        setSession(s);
        setPreview(s.notebook?.markdown ?? null);
      })
      .catch((e) => setErr(e instanceof Error ? e.message : "Load failed"));
  }, [sessionId]);

  const isCells =
    (session?.domain_hint ?? "").includes("cell") ||
    (session?.scene?.suggested_domain ?? "").includes("cell");

  return (
    <>
      <PageHeader
        title="Lab notebook"
        subtitle="Markdown export after accept — pendulum law card or biology.cells template."
        actions={
          sessionId && session?.status === "accepted" ? (
            <a className="btn secondary" href={notebookDownloadUrl(sessionId)} download>
              Download .md
            </a>
          ) : null
        }
      />

      {!sessionId ? (
        <div className="empty-state">
          <p>No session selected. Run a demo in the lab first.</p>
          <Link href="/lab?demo=1" className="btn">
            Run demo
          </Link>
        </div>
      ) : err ? (
        <div className="alert alert--danger">{err}</div>
      ) : !session ? (
        <p className="meta">Loading…</p>
      ) : session.status !== "accepted" || !session.notebook ? (
        <div className="panel">
          <p>Session {session.id.slice(0, 8)} is not accepted yet.</p>
          <AcceptGateHint session={session} />
          <Link href={`/session/${session.id}`} className="btn secondary" style={{ marginTop: "1rem", display: "inline-block" }}>
            Open session
          </Link>
        </div>
      ) : (
        <>
          <div className="panel">
            <KatexMath latex={session.notebook.law_latex} display />
            <p className="meta">
              params {JSON.stringify(session.notebook.params)} · error bars{" "}
              {JSON.stringify(session.notebook.error_bars)}
            </p>
          </div>
          {isCells ? (
            <p className="meta">
              Cells domain:{" "}
              <a href={cellsNotebookDownloadUrl(session.id)} download>
                download cells notebook template
              </a>
            </p>
          ) : null}
          <pre
            className="panel"
            style={{
              whiteSpace: "pre-wrap",
              fontFamily: "var(--font-mono)",
              fontSize: "0.78rem",
              maxHeight: 480,
              overflow: "auto",
            }}
          >
            {preview}
          </pre>
        </>
      )}

      <RecentPicker onPick={setSessionId} current={sessionId} />
    </>
  );
}

function AcceptGateHint({ session }: { session: Session }) {
  const reasons = session.law_gate?.reasons;
  if (!reasons?.length) return <p className="meta">Complete the pipeline and pass held-out gates to export.</p>;
  return <p className="meta">Gates: {reasons.join("; ")}</p>;
}

function RecentPicker({ onPick, current }: { onPick: (id: string) => void; current: string | null }) {
  const [recent, setRecent] = useState<string[]>([]);
  useEffect(() => {
    setRecent(getRecentSessionIds());
  }, [current]);

  if (recent.length < 2) return null;

  return (
    <div className="panel panel--flat" style={{ marginTop: "1rem" }}>
      <h3>Recent sessions</h3>
      <div className="page-header__actions">
        {recent.map((id) => (
          <button
            key={id}
            type="button"
            className={`btn secondary${id === current ? " winner" : ""}`}
            onClick={() => onPick(id)}
          >
            {id.slice(0, 8)}
          </button>
        ))}
      </div>
    </div>
  );
}
