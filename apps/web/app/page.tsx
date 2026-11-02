"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { FixtureModeBanner } from "@/components/FixtureModeBanner";
import { GhostCanvas } from "@/components/GhostCanvas";
import { PipelineStepper } from "@/components/PipelineStepper";
import { SessionErrorPanel } from "@/components/SessionErrorPanel";
import { TrackOverlay } from "@/components/TrackOverlay";
import {
  connectSessionEvents,
  createSession,
  health,
  resumeSession,
  runSessionWithProgress,
} from "@/lib/api";
import type { PipelineStage } from "@/lib/pipeline";
import type { StepperKey } from "@/lib/pipeline";
import type { HealthInfo, Session } from "@/lib/types";

function eventLine(e: { stage?: string; message?: string; event?: string; error?: string }): string {
  const head = e.stage || e.event || "event";
  const body = e.message || e.error || "";
  return body ? `${head} — ${body}` : head;
}

export default function HomePage() {
  const [session, setSession] = useState<Session | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [healthInfo, setHealthInfo] = useState<HealthInfo | null>(null);
  const [activeStep, setActiveStep] = useState<StepperKey>("created");
  const [progressLabel, setProgressLabel] = useState<string | null>(null);
  const disconnectRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    health()
      .then(setHealthInfo)
      .catch(() => setHealthInfo({ ok: false }));
    return () => disconnectRef.current?.();
  }, []);

  const ghost = session?.imagination?.[0]?.ghost_polyline;
  const winner = session?.hypotheses?.find((h) => h.status === "winner");

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

  function attachEvents(sessionId: string) {
    disconnectRef.current?.();
    disconnectRef.current = connectSessionEvents(sessionId, {
      onActiveStep: setActiveStep,
      onStageStarted: (d) => setProgressLabel(d.stage ? `${d.stage}…` : "Running…"),
      onStageCompleted: () => setProgressLabel(null),
      onStageFailed: (d) => setProgressLabel(d.error ? String(d.error).slice(0, 80) : "Stage failed"),
    });
  }

  async function runPipeline(sessionId: string) {
    return runSessionWithProgress(sessionId, ({ stage, phase, session: s }) => {
      setSession(s);
      if (phase === "started") {
        setProgressLabel(`${stage}…`);
      }
    });
  }

  async function onRun(file?: File) {
    setBusy(true);
    setErr(null);
    setProgressLabel("Creating session…");
    try {
      const created = await createSession(file);
      setSession(created);
      setActiveStep("created");
      attachEvents(created.id);
      const ran = await runPipeline(created.id);
      setSession(ran);
      setProgressLabel(null);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Run failed");
    } finally {
      setBusy(false);
    }
  }

  async function onResume(fromStage: PipelineStage) {
    if (!session) return;
    setBusy(true);
    setErr(null);
    attachEvents(session.id);
    try {
      const ran = await resumeSession(session.id, fromStage);
      setSession(ran);
      if (ran.status === "failed") {
        throw new Error(ran.error || "Resume failed");
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Resume failed");
    } finally {
      setBusy(false);
      setProgressLabel(null);
    }
  }

  const showStepper = Boolean(session) || busy;

  return (
    <main>
      <FixtureModeBanner
        fixtureMode={Boolean(healthInfo?.fixture_mode)}
        fixtureRecord={Boolean(healthInfo?.fixture_record)}
      />
      <section className="hero shell">
        <p className="meta" style={{ marginBottom: "1.25rem" }}>
          META GLOBAL AI DEVELOPER HACKATHON · INDIE · PUSH THE FRONTIER
        </p>
        <h1 className="brand">HYPATIA</h1>
        <p className="tag">
          The camera that does science. Watch anything move, discover the law, prove it by predicting
          the future, then ask for the one experiment that matters.
        </p>
        <div className="cta-row">
          <button className="btn" disabled={busy} onClick={() => onRun()}>
            {busy ? progressLabel || "Running scientific loop…" : "Run desk pendulum demo"}
          </button>
          <label className="btn secondary" style={{ cursor: busy ? "wait" : "pointer" }}>
            Upload clip
            <input
              type="file"
              accept="video/*,image/*"
              hidden
              disabled={busy}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void onRun(f);
              }}
            />
          </label>
        </div>
        {busy && progressLabel ? (
          <p className="meta progress-line" aria-live="polite">
            {progressLabel}
          </p>
        ) : null}
        <p className="meta" style={{ marginTop: "1rem" }}>
          mode: {String(healthInfo?.fixture_mode ? "fixture-ready" : "live-capable")} · deploy: Meta
          API → Modal → Baseten/Fireworks → AWS
        </p>
      </section>

      <section className="lab shell" id="lab">
        {showStepper && session ? (
          <PipelineStepper session={session} activeStep={activeStep} busy={busy} />
        ) : null}

        {err ? (
          <SessionErrorPanel
            message={err}
            session={session}
            busy={busy}
            onResume={session?.status === "failed" ? onResume : undefined}
          />
        ) : null}

        {session?.scene && (
          <div className="panel" style={{ marginBottom: "1rem" }}>
            <h2>Observer — SceneBrief</h2>
            <p className="meta">
              domain {session.scene.suggested_domain} · SAM prompts for measurer
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
              {session.scene.sam_prompts.map((p) => (
                <span key={p} className="pill">
                  {p}
                </span>
              ))}
            </div>
            {session.scene.candidate_variables?.length ? (
              <p className="meta" style={{ marginTop: "0.75rem" }}>
                variables: {session.scene.candidate_variables.join(", ")}
              </p>
            ) : null}
          </div>
        )}

        {session?.tracks?.length ? (
          <div className="panel" style={{ marginBottom: "1rem" }}>
            <h2>Measurer — SAM track</h2>
            <TrackOverlay tracks={session.tracks} />
          </div>
        ) : null}

        <div className="grid two">
          <div className="panel">
            <h2>Imagination audit</h2>
            <div className="stage">
              <GhostCanvas real={realProxy} ghost={ghost} />
            </div>
            {session?.imagination?.[0] && (
              <p className="meta" style={{ marginTop: "0.75rem" }}>
                source={session.imagination[0].source} · SAM-style audit error ≈{" "}
                {session.imagination[0].audit_error_m} m · session {session.id.slice(0, 8)}
              </p>
            )}
            {session?.scene?.narration && (
              <p style={{ marginTop: "0.85rem", color: "var(--fog)" }}>{session.scene.narration}</p>
            )}
          </div>

          <div className="panel">
            <h2>Rival theories</h2>
            <div className="cards">
              {(session?.hypotheses || []).map((h) => (
                <div key={h.id} className={`card ${h.status}`}>
                  <div className="latex">{h.form_latex}</div>
                  <div className="meta">
                    {h.form_plain} · held-out {h.heldout_score.toFixed(3)} · {h.status}
                  </div>
                  <div className="meta">{JSON.stringify(h.params)}</div>
                </div>
              ))}
              {!session && <p className="meta">Run a session to spawn the hypothesis swarm.</p>}
            </div>
          </div>
        </div>

        <div className="grid two">
          <div className="panel">
            <h2>Next experiment</h2>
            {session?.experiment ? (
              <>
                <p style={{ fontSize: "1.15rem", color: "var(--law)", marginTop: 0 }}>
                  {session.experiment.instruction}
                </p>
                <p className="meta">{session.experiment.rationale}</p>
                <div style={{ marginTop: "0.75rem" }}>
                  {Object.entries(session.experiment.expected_outcomes).map(([k, v]) => (
                    <div key={k} className="meta">
                      <span className="pill">{k}</span>
                      {v}
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="meta">The PI will ask for the highest-information test.</p>
            )}
          </div>

          <div className="panel">
            <h2>Lab notebook</h2>
            {winner ? (
              <>
                <p className="latex" style={{ fontFamily: "var(--font-display)", fontSize: "1.4rem" }}>
                  {session?.notebook?.law_latex || winner.form_latex}
                </p>
                <p className="meta">params {JSON.stringify(session?.notebook?.params || winner.params)}</p>
                <p className="meta">
                  error bars {JSON.stringify(session?.notebook?.error_bars || {})} · meta calls{" "}
                  {session?.meta_calls?.length || 0}
                </p>
              </>
            ) : (
              <p className="meta">Accepted law + error bars land here after held-out rivalry.</p>
            )}
            <div className="events" style={{ marginTop: "0.75rem" }}>
              {(session?.events || []).map((e, i) => (
                <div key={`${e.stage ?? e.event}-${i}`}>{eventLine(e)}</div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
