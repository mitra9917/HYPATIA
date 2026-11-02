"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AcceptGatePanel } from "@/components/AcceptGatePanel";
import { GhostCanvas } from "@/components/GhostCanvas";
import { HypothesisCard } from "@/components/HypothesisCard";
import { HypothesisLeaderboard } from "@/components/HypothesisLeaderboard";
import { KatexMath } from "@/components/KatexMath";
import { ObserverNarration } from "@/components/ObserverNarration";
import { PageHeader } from "@/components/shell/PageHeader";
import { TrackOverlay } from "@/components/TrackOverlay";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import { VoiceMic } from "@/components/VoiceMic";
import {
  getSession,
  imaginationFrameUrl,
  notebookDownloadUrl,
  submitExperimentResult,
} from "@/lib/api";
import { commitLaw } from "@/lib/lab-run";
import type { Hypothesis, Session } from "@/lib/types";
import { rememberSessionId } from "@/lib/recent-sessions";

function demoGLine(h: Hypothesis): string | undefined {
  if (h.params.g == null) return undefined;
  const ci = h.param_ci?.g;
  if (ci) {
    const mid = (ci[0] + ci[1]) / 2;
    const half = (ci[1] - ci[0]) / 2;
    return `g ≈ ${mid.toFixed(1)} ± ${half.toFixed(1)} m/s²`;
  }
  return `g ≈ ${h.params.g.toFixed(1)} m/s²`;
}

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = String(params.id ?? "");
  const [session, setSession] = useState<Session | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!sessionId) return;
    rememberSessionId(sessionId);
    void getSession(sessionId)
      .then(setSession)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load session"));
  }, [sessionId]);

  const ghost = session?.imagination?.[0]?.ghost_polyline;
  const winner = session?.hypotheses?.find((h) => h.status === "winner");
  const canCommitLaw = Boolean(session?.law_gate?.ok && session.status !== "accepted");

  const realProxy = useMemo(() => {
    const pts = session?.tracks?.[0]?.points;
    if (pts?.length) {
      return pts
        .filter((p) => p.x_m != null && p.y_m != null)
        .map((p) => ({ x_m: p.x_m as number, y_m: p.y_m as number }));
    }
    if (!ghost?.length) return undefined;
    return ghost.map((p, i) => ({
      x_m: p.x_m * 0.98 + (i % 7) * 0.0008,
      y_m: p.y_m * 0.98,
    }));
  }, [session?.tracks, ghost]);

  if (err) {
    return (
      <div className="alert alert--danger" role="alert">
        {err}
      </div>
    );
  }

  if (!session) {
    return <p className="meta">Loading session…</p>;
  }

  return (
    <>
      <PageHeader
        title={`Session ${session.id.slice(0, 8)}`}
        subtitle={`${session.status} · ${session.mode} · ${session.source_type ?? "fixture"}`}
        actions={
          session.status === "accepted" ? (
            <a className="btn secondary" href={notebookDownloadUrl(session.id)} download>
              Download notebook
            </a>
          ) : canCommitLaw ? (
            <button
              type="button"
              className="btn"
              disabled={busy}
              onClick={() => {
                setBusy(true);
                void commitLaw(session.id)
                  .then(setSession)
                  .catch((ex) => setErr(String(ex)))
                  .finally(() => setBusy(false));
              }}
            >
              Commit law
            </button>
          ) : null
        }
      />

      <div className="grid two">
        <div className="panel">
          <h2>Observer · SAM tracking</h2>
          <ObserverNarration narration={session.scene?.narration ?? ""} domain={session.scene?.suggested_domain} />
          {session.tracks?.length ? (
            <>
              <TrackOverlay tracks={session.tracks} />
              <TrajectoryChart points={session.tracks[0]?.points} />
            </>
          ) : null}
        </div>
        <div className="panel">
          <h2>Imagination audit</h2>
          <div className="stage">
            <GhostCanvas real={realProxy} ghost={ghost} />
          </div>
          {session.imagination?.[0] ? (
            <>
              <p className="meta" style={{ marginTop: "0.75rem" }}>
                source={session.imagination[0].source} · audit error ≈ {session.imagination[0].audit_error_m} m
                {session.imagination[0].audit_iou != null
                  ? ` · IoU ${session.imagination[0].audit_iou.toFixed(3)}`
                  : ""}
              </p>
              <img
                src={imaginationFrameUrl(session.id, 0)}
                alt="Muse Image ghost frame or geometric placeholder"
                style={{ maxWidth: "100%", marginTop: "0.5rem", borderRadius: 8, border: "1px solid var(--line)" }}
              />
            </>
          ) : null}
        </div>
      </div>

      <div className="grid two">
        <div className="panel">
          <h2>Rival theories</h2>
          <HypothesisLeaderboard hypotheses={session.hypotheses} />
          <div className="cards" style={{ marginTop: "1rem" }}>
            {session.hypotheses.map((h) => (
              <HypothesisCard key={h.id} hypothesis={h} demoLine={demoGLine(h)} />
            ))}
          </div>
        </div>
        <div className="panel">
          <h2>Accept gate</h2>
          <AcceptGatePanel session={session} />
          {winner ? (
            <div style={{ marginTop: "1rem" }}>
              <KatexMath latex={session.notebook?.law_latex || winner.form_latex} display />
              <p className="meta">{demoGLine(winner)}</p>
            </div>
          ) : null}
        </div>
      </div>

      <div className="grid two">
        <div className="panel">
          <h2>Next experiment · Muse Wonder</h2>
          {session.experiment ? (
            <>
              <p style={{ fontSize: "1.05rem", marginTop: 0 }}>{session.experiment.instruction}</p>
              <p className="meta">{session.experiment.rationale}</p>
              {Object.entries(session.experiment.expected_outcomes).map(([k, v]) => (
                <div key={k} className="meta">
                  <span className="pill">{k}</span> {v}
                </div>
              ))}
            </>
          ) : (
            <p className="meta">Experiment proposal appears after the experiment stage.</p>
          )}
          {session.experiment && !session.experiment_result ? (
            <form
              style={{ marginTop: "0.75rem" }}
              onSubmit={(e) => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                const ratio = parseFloat(String(fd.get("ratio") || ""));
                void submitExperimentResult(session.id, {
                  notes: String(fd.get("notes") || ""),
                  observed_period_ratio: Number.isFinite(ratio) ? ratio : undefined,
                  supports_winner: true,
                }).then(setSession);
              }}
            >
              <label className="meta">
                Period ratio <input name="ratio" type="number" step="0.01" defaultValue="1.41" />
              </label>
              <button type="submit" className="btn secondary" style={{ marginLeft: "0.5rem" }}>
                Submit result
              </button>
            </form>
          ) : null}
          <VoiceMic sessionId={session.id} />
        </div>
        <div className="panel">
          <h2>PI plans · meta calls</h2>
          {Object.entries(session.pi_plans ?? {}).length ? (
            <ul style={{ paddingLeft: "1.1rem", margin: 0 }}>
              {Object.entries(session.pi_plans ?? {}).map(([phase, plan]) => (
                <li key={phase} style={{ marginBottom: "0.65rem" }}>
                  <strong>{phase}</strong>
                  <div className="meta">{plan.narration}</div>
                  {plan.tools?.length ? (
                    <div>
                      {plan.tools.map((t) => (
                        <span key={t} className="pill">
                          {t}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : (
            <p className="meta">Wonder PI phase plans populate during experiment (fixture_pi in replay mode).</p>
          )}
          <p className="meta" style={{ marginTop: "0.75rem" }}>
            {session.meta_calls?.length ?? 0} Meta calls logged
          </p>
          <div className="events" style={{ marginTop: "0.5rem" }}>
            {(session.events ?? []).slice(-12).map((e, i) => (
              <div key={`${e.stage}-${i}`}>
                {e.stage || e.event} — {e.message || e.error || ""}
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="meta">
        <Link href="/lab">← Back to lab</Link> · <Link href="/notebook">Notebook view</Link>
      </p>
    </>
  );
}
