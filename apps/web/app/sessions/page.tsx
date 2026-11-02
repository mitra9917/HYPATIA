"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PageHeader } from "@/components/shell/PageHeader";
import { getSession, listLaws } from "@/lib/api";
import type { LawSummary, Session } from "@/lib/types";
import { getRecentSessionIds } from "@/lib/recent-sessions";

type Row = { id: string; status?: string; mode?: string; source?: string; hasLaw?: boolean };

export default function SessionsPage() {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const recent = getRecentSessionIds();
      const laws = await listLaws().catch(() => [] as LawSummary[]);
      const lawIds = new Set(laws.map((l) => l.session_id));
      const ids = [...new Set([...recent, ...laws.map((l) => l.session_id)])].slice(0, 20);
      const loaded: Row[] = [];
      for (const id of ids) {
        try {
          const s: Session = await getSession(id);
          loaded.push({
            id: s.id,
            status: s.status,
            mode: s.mode,
            source: s.source_type,
            hasLaw: lawIds.has(id) || Boolean(s.notebook),
          });
        } catch {
          loaded.push({ id, status: "unknown" });
        }
      }
      setRows(loaded);
      setLoading(false);
    }
    void load();
  }, []);

  return (
    <>
      <PageHeader
        title="Sessions"
        subtitle="Recent browser sessions plus accepted laws from the in-memory store (no global list API)."
        actions={
          <Link href="/lab?demo=1" className="btn">
            New demo run
          </Link>
        }
      />
      {loading ? (
        <p className="meta">Loading…</p>
      ) : rows.length === 0 ? (
        <div className="empty-state">
          <p>No sessions yet. Run the desk pendulum demo to create one.</p>
          <Link href="/lab" className="btn">
            Open lab
          </Link>
        </div>
      ) : (
        <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--line)", textAlign: "left" }}>
                <th style={{ padding: "0.75rem 1rem" }}>Session</th>
                <th>Status</th>
                <th>Mode</th>
                <th>Source</th>
                <th>Law</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} style={{ borderBottom: "1px solid var(--line)" }}>
                  <td style={{ padding: "0.65rem 1rem" }}>
                    <Link href={`/session/${r.id}`}>{r.id.slice(0, 8)}…</Link>
                  </td>
                  <td>{r.status ?? "—"}</td>
                  <td>{r.mode ?? "—"}</td>
                  <td>{r.source ?? "—"}</td>
                  <td>{r.hasLaw ? "accepted" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
