"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ContributorModeBanner } from "@/components/ContributorModeBanner";
import { EthicsConsentBanner } from "@/components/EthicsConsentBanner";
import { FixtureModeBanner } from "@/components/FixtureModeBanner";
import { OpsModeBanner } from "@/components/OpsModeBanner";
import { PageHeader } from "@/components/shell/PageHeader";
import {
  analyzeVeritas,
  createCellsSession,
  listTools,
  runToolsmithTest,
} from "@/lib/api";
import type { ToolLibraryEntry, VeritasResult } from "@/lib/types";
import { useHealth } from "@/lib/use-health";

export default function SettingsPage() {
  const { healthInfo, healthErr, refresh, loading } = useHealth(30_000);
  const [consent, setConsent] = useState(false);
  const [tools, setTools] = useState<ToolLibraryEntry[]>([]);
  const [veritas, setVeritas] = useState<VeritasResult | null>(null);
  const [toolsmithMsg, setToolsmithMsg] = useState<string | null>(null);
  const [cellsId, setCellsId] = useState<string | null>(null);

  useEffect(() => {
    void listTools()
      .then(setTools)
      .catch(() => setTools([]));
  }, []);

  return (
    <>
      <PageHeader
        title="Settings & ops"
        subtitle="Fixture replay, live Meta paths, contributor routing, ethics consent, and deploy health."
        actions={
          <button type="button" className="btn secondary" disabled={loading} onClick={refresh}>
            Refresh health
          </button>
        }
      />

      {healthErr ? (
        <div className="alert alert--danger" role="alert">
          {healthErr}
        </div>
      ) : null}

      <div className="settings-grid">
        <div className="panel">
          <h2>API health</h2>
          {healthInfo ? (
            <ul style={{ margin: 0, paddingLeft: "1.1rem", fontSize: "0.9rem" }}>
              <li>Service: {healthInfo.service ?? "hypatia-api"}</li>
              <li>Session store: {healthInfo.session_store ?? "memory"}</li>
              <li>Pipeline: {(healthInfo.pipeline_stages ?? []).join(" → ")}</li>
              <li>Observer model: {healthInfo.model_router?.observer ?? "—"}</li>
              <li>Deploy priority: Meta API → Modal → partner inference → AWS</li>
            </ul>
          ) : (
            <p className="meta">Checking…</p>
          )}
        </div>

        <div className="panel">
          <h2>Ops mode</h2>
          <OpsModeBanner ops={healthInfo?.ops} onModeChange={refresh} />
          <FixtureModeBanner
            fixtureMode={Boolean(healthInfo?.fixture_mode ?? healthInfo?.ops?.fixture_mode)}
            fixtureRecord={Boolean(healthInfo?.fixture_record)}
          />
          <ContributorModeBanner
            active={Boolean(
              healthInfo?.contributor_policy?.meta_use_contributor || healthInfo?.model_router?.use_contributor,
            )}
            tier={healthInfo?.contributor_policy?.observer_spark_tier}
          />
        </div>

        <div className="panel">
          <h2>Public demo consent</h2>
          <EthicsConsentBanner checked={consent} onChange={setConsent} />
          <p className="meta" style={{ marginTop: "0.75rem" }}>
            Required before upload or webcam burst (<code>upload_consent=true</code> on POST /api/sessions).
          </p>
        </div>

        <div className="panel">
          <h2>Tool library & Toolsmith</h2>
          {tools.length ? (
            <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
              {tools.map((t) => (
                <li key={t.id}>
                  <strong>{t.title}</strong>
                  <span className="meta"> · {t.domain}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="meta">No promoted tools yet.</p>
          )}
          <button
            type="button"
            className="btn secondary"
            style={{ marginTop: "0.75rem" }}
            onClick={() =>
              void runToolsmithTest().then((r) =>
                setToolsmithMsg(r.ok ? `OK: ${r.stdout?.trim()}` : `Failed: ${r.stderr?.trim() || r.returncode}`),
              )
            }
          >
            Run Toolsmith test (fixture track)
          </button>
          {toolsmithMsg ? <p className="meta">{toolsmithMsg}</p> : null}
        </div>

        <div className="panel">
          <h2>VERITAS integrity</h2>
          <p className="meta">Fixture fake-physics clip — POST /api/veritas/analyze</p>
          <button
            type="button"
            className="btn secondary"
            onClick={() => void analyzeVeritas().then(setVeritas)}
          >
            Analyze fixture clip
          </button>
          {veritas ? (
            <div style={{ marginTop: "0.75rem" }}>
              <p>
                <strong>{veritas.verdict}</strong> — {veritas.headline}
              </p>
              <p className="meta">{veritas.detail}</p>
              <p className="meta">
                break frame {veritas.break_frame} · measured g {veritas.measured_g_m_s2} m/s²
              </p>
            </div>
          ) : null}
        </div>

        <div className="panel">
          <h2>Biology.cells domain</h2>
          <p className="meta">Create session with domain_hint=biology.cells for logistic notebook template.</p>
          <button
            type="button"
            className="btn secondary"
            onClick={() =>
              void createCellsSession().then((s) => {
                setCellsId(s.id);
              })
            }
          >
            Create cells session
          </button>
          {cellsId ? (
            <p className="meta" style={{ marginTop: "0.5rem" }}>
              Session {cellsId.slice(0, 8)} — run observe in API, then{" "}
              <Link href={`/session/${cellsId}`}>open session</Link>
            </p>
          ) : null}
        </div>
      </div>
    </>
  );
}
