"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { KatexMath } from "@/components/KatexMath";
import { PageHeader } from "@/components/shell/PageHeader";
import { getSession, listLaws } from "@/lib/api";
import { filterGroupedLaws, groupLaws } from "@/lib/laws";
import type { LawSummary } from "@/lib/types";

export default function LibraryPage() {
  const [laws, setLaws] = useState<LawSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void listLaws()
      .then(setLaws)
      .catch(() => setLaws([]))
      .finally(() => setLoading(false));
  }, []);

  const groups = useMemo(() => filterGroupedLaws(groupLaws(laws), query), [laws, query]);

  return (
    <>
      <PageHeader
        title="Law library"
        subtitle="Accepted laws from this API store — deduplicated by formula, grouped by domain, rendered with KaTeX."
      />
      <input
        className="search-input"
        type="search"
        placeholder="Search laws, domains, or session id…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search laws"
      />
      {loading ? (
        <p className="meta">Loading library…</p>
      ) : groups.length === 0 ? (
        <div className="empty-state">
          <h2>No laws yet</h2>
          <p>Run a desk pendulum demo in the lab and pass the accept gate to populate the library.</p>
          <Link href="/lab?demo=1" className="btn">
            Run demo
          </Link>
        </div>
      ) : (
        <div className="law-grid">
          {groups.map((g) => (
            <article key={g.key} className="law-card">
              <div className="law-card__domain">
                <span className="pill">{g.domain}</span>
                {g.entries.length > 1 ? (
                  <span className="meta"> {g.entries.length} sessions</span>
                ) : null}
              </div>
              <KatexMath latex={g.law_latex} display />
              <p className="meta" style={{ marginTop: "0.5rem" }}>
                g ≈ {g.best.params.g?.toFixed?.(2) ?? "—"} · mode {g.best.mode}
                {g.best.error_bars?.g != null ? ` · ±${g.best.error_bars.g}` : ""}
              </p>
              <div style={{ marginTop: "0.75rem" }}>
                {g.entries.slice(0, 3).map((e) => (
                  <Link key={e.session_id} href={`/session/${e.session_id}`} className="meta" style={{ display: "block" }}>
                    Session {e.session_id.slice(0, 8)} →
                  </Link>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
