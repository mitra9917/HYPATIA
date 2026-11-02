"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listLaws } from "@/lib/api";
import { getActiveSessionId } from "@/lib/recent-sessions";
import { useHealth } from "@/lib/use-health";

export default function HomePage() {
  const { healthInfo, healthErr, loading, refresh } = useHealth();
  const [lawCount, setLawCount] = useState<number | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    setActiveId(getActiveSessionId());
    void listLaws()
      .then((l) => setLawCount(l.length))
      .catch(() => setLawCount(null));
  }, []);

  const fixture = Boolean(healthInfo?.fixture_mode ?? healthInfo?.ops?.fixture_mode);

  return (
    <>
      <section className="home-hero">
        <p className="home-hero__eyebrow">Meta Global AI Developer Hackathon · Indie · Push the Frontier</p>
        <h1 className="home-hero__title">The camera that does science.</h1>
        <p className="home-hero__lead">
          Watch motion, measure in SI units, rank rival laws on held-out data, audit the imagined future, and ask
          Muse Wonder for the one experiment that matters.
        </p>
        <div className="page-header__actions">
          <Link href="/lab" className="btn">
            Open lab
          </Link>
          <Link href="/lab?demo=1" className="btn secondary">
            Run desk pendulum demo
          </Link>
        </div>
        <div className="stat-row">
          <div className="stat">
            <span className="stat__value">{loading ? "…" : healthInfo?.ok ? "Online" : "Offline"}</span>
            <span className="stat__label">API health</span>
          </div>
          <div className="stat">
            <span className="stat__value">{fixture ? "Fixture" : "Live-capable"}</span>
            <span className="stat__label">Ops mode</span>
          </div>
          <div className="stat">
            <span className="stat__value">{lawCount ?? "—"}</span>
            <span className="stat__label">Laws in library</span>
          </div>
        </div>
        {healthErr ? (
          <div className="alert alert--danger" style={{ marginTop: "1.25rem" }} role="alert">
            API not connected: {healthErr}. Run <code>./scripts/run_api_local.sh</code> and set{" "}
            <code>NEXT_PUBLIC_API_ORIGIN=http://127.0.0.1:8000</code> in <code>apps/web/.env.local</code>.
            <button type="button" className="btn secondary" style={{ marginLeft: "0.75rem" }} onClick={refresh}>
              Retry
            </button>
          </div>
        ) : null}
      </section>

      <div className="home-grid">
        <Link href="/lab" className="home-card">
          <h3>Lab</h3>
          <p>Guided stepper: capture → track → rivals → ghost → experiment → accept gate.</p>
        </Link>
        <Link href={activeId ? `/session/${activeId}` : "/sessions"} className="home-card">
          <h3>Session</h3>
          <p>Trajectory plots, imagination audit, PI plans, voice, and notebook export.</p>
        </Link>
        <Link href="/library" className="home-card">
          <h3>Law library</h3>
          <p>KaTeX-rendered laws, deduplicated by domain with search.</p>
        </Link>
        <Link href="/settings" className="home-card">
          <h3>Settings</h3>
          <p>Fixture / live / hybrid, Spark Contributor, ethics consent, deploy health.</p>
        </Link>
      </div>
    </>
  );
}
