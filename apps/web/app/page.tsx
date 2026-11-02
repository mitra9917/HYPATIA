"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ContributorModeBanner } from "@/components/ContributorModeBanner";
import { EthicsConsentBanner } from "@/components/EthicsConsentBanner";
import { FixtureModeBanner } from "@/components/FixtureModeBanner";
import { LawLibraryPanel } from "@/components/LawLibraryPanel";
import { OpsModeBanner } from "@/components/OpsModeBanner";
import { GhostCanvas } from "@/components/GhostCanvas";
import { PipelineStepper } from "@/components/PipelineStepper";
import { SessionErrorPanel } from "@/components/SessionErrorPanel";
import { TrackOverlay } from "@/components/TrackOverlay";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import { WebcamCapture } from "@/components/WebcamCapture";
import {
  acceptLaw,
  connectSessionEvents,
  createSession,
  getSession,
  health,
  notebookDownloadUrl,
  resumeSession,
  runSessionWithProgress,
  submitExperimentResult,
} from "@/lib/api";
import { HypothesisCard } from "@/components/HypothesisCard";
import { ObserverNarration } from "@/components/ObserverNarration";
import { VoiceMic } from "@/components/VoiceMic";
import type { PipelineStage } from "@/lib/pipeline";
import type { StepperKey } from "@/lib/pipeline";
import type { HealthInfo, Hypothesis, Session } from "@/lib/types";

function demoGLine(h: Hypothesis): string | undefined {
  if (h.params.g == null) return undefined;
  const ci = h.param_ci?.g;
  if (ci) {
    const mid = (ci[0] + ci[1]) / 2;
    const half = (ci[1] - ci[0]) / 2;
    return `T = 2π√(L/g), g ≈ ${mid.toFixed(1)} ± ${half.toFixed(1)}`;
  }
  return `T = 2π√(L/g), g ≈ ${h.params.g.toFixed(1)}`;
}

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
  const [uploadConsent, setUploadConsent] = useState(false);
  const disconnectRef = useRef<(() => void) | null>(null);

  function refreshHealth() {
    void health()
      .then(setHealthInfo)
      .catch(() => setHealthInfo({ ok: false }));
  }

  useEffect(() => {
    refreshHealth();
    return () => disconnectRef.current?.();
  }, []);

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

  function attachEvents(sessionId: string) {
    disconnectRef.current?.();
    disconnectRef.current = connectSessionEvents(sessionId, {
      onActiveStep: setActiveStep,
      onStageStarted: (d) => setProgressLabel(d.stage ? `${d.stage}…` : "Running…"),
      onStageCompleted: (d) => {
        setProgressLabel(null);
        if (d.stage === "observe") {
          void getSession(sessionId).then(setSession).catch(() => {});
        }
      },
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

  async function onRun(file?: File, source: "upload" | "webcam" | "fixture" = "fixture") {
    if ((source === "upload" || source === "webcam") && !uploadConsent) {
      setErr("Check the ethics consent box before upload or webcam capture.");
      return;
    }
    setBusy(true);
    setErr(null);
    setProgressLabel("Creating session…");
    try {
      const created =
        source === "fixture" && !file
          ? await createSession()
          : await createSession(file, source === "webcam" ? "webcam" : "upload", {
              uploadConsent: source === "fixture" ? true : uploadConsent,
            });
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
      <ContributorModeBanner
        active={Boolean(
          healthInfo?.contributor_policy?.meta_use_contributor ||
            healthInfo?.model_router?.use_contributor,
        )}
        tier={healthInfo?.contributor_policy?.observer_spark_tier}
      />
      <FixtureModeBanner
        fixtureMode={Boolean(healthInfo?.fixture_mode ?? healthInfo?.ops?.fixture_mode)}
        fixtureRecord={Boolean(healthInfo?.fixture_record)}
      />
      <OpsModeBanner ops={healthInfo?.ops} onModeChange={refreshHealth} />
      <EthicsConsentBanner checked={uploadConsent} onChange={setUploadConsent} />
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
          <button className="btn" disabled={busy} onClick={() => void onRun(undefined, "fixture")}>
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
                if (f) void onRun(f, "upload");
              }}
            />
          </label>
          <WebcamCapture disabled={busy} onCapture={(file) => void onRun(file, "webcam")} />
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

        {session?.library_hint ? (
          <p className="meta" style={{ marginBottom: "1rem" }}>
            {session.library_hint.message}
            {session.library_hint.matches?.[0]?.law_latex
              ? ` · prior: ${session.library_hint.matches[0].law_latex}`
              : ""}
          </p>
        ) : null}

        {session && (
          <div className="panel observer-panel" style={{ marginBottom: "1rem" }}>
            <h2>Observer — what the camera sees</h2>
            <div className={session.tracks?.length ? "observer-lab-grid" : undefined}>
              <ObserverNarration
                narration={session.scene?.narration ?? ""}
                domain={session.scene?.suggested_domain}
                placeholder={
                  session.scene?.narration ? undefined : "Spark Observer narrates after the watch step…"
                }
              />
              {session.tracks?.length ? <TrackOverlay tracks={session.tracks} /> : null}
            </div>
            {session.scene && !session.tracks?.length ? (
              <>
                <p className="meta" style={{ marginTop: "0.75rem" }}>
                  SAM prompts for measurer
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
                  {session.scene.sam_prompts.map((p) => (
                    <span key={p} className="pill">
                      {p}
                    </span>
                  ))}
                </div>
              </>
            ) : null}
            {session.tracks?.length ? (
              <TrajectoryChart points={session.tracks[0]?.points} title="Pendulum angle vs time" />
            ) : null}
          </div>
        )}

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
          </div>

          <div className="panel">
            <h2>Rival theories</h2>
            <div className="cards">
              {(session?.hypotheses || []).map((h) => (
                <HypothesisCard key={h.id} hypothesis={h} demoLine={demoGLine(h)} />
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
            {session?.experiment && !session.experiment_result ? (
              <form
                className="meta"
                style={{ marginTop: "0.75rem" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  const fd = new FormData(e.currentTarget);
                  const ratio = parseFloat(String(fd.get("ratio") || ""));
                  void submitExperimentResult(session.id, {
                    notes: String(fd.get("notes") || "Recorded in lab"),
                    observed_period_ratio: Number.isFinite(ratio) ? ratio : undefined,
                    supports_winner: true,
                  })
                    .then(setSession)
                    .catch((ex) => setErr(String(ex)));
                }}
              >
                <label>
                  Period ratio after experiment{" "}
                  <input name="ratio" type="number" step="0.01" defaultValue="1.41" />
                </label>
                <input name="notes" type="text" placeholder="Notes" style={{ marginLeft: "0.5rem" }} />
                <button type="submit" className="btn secondary" style={{ marginLeft: "0.5rem" }}>
                  Submit result
                </button>
              </form>
            ) : null}
            {session?.experiment_result ? (
              <p className="meta" style={{ marginTop: "0.5rem" }}>
                Result logged · ratio {session.experiment_result.observed_period_ratio ?? "—"}×
              </p>
            ) : null}
            <VoiceMic sessionId={session?.id ?? null} />
          </div>

          <div className="panel">
            <h2>Lab notebook</h2>
            {winner ? (
              <>
                <p className="latex" style={{ fontFamily: "var(--font-display)", fontSize: "1.4rem" }}>
                  {session?.notebook?.law_latex || winner.form_latex}
                </p>
                <p className="meta">{demoGLine(winner) || `params ${JSON.stringify(winner.params)}`}</p>
                <p className="meta">
                  error bars {JSON.stringify(session?.notebook?.error_bars || {})} · meta calls{" "}
                  {session?.meta_calls?.length || 0}
                </p>
                <button
                  type="button"
                  className="btn"
                  style={{ marginTop: "0.75rem" }}
                  disabled={!canCommitLaw || busy}
                  onClick={() => {
                    if (!session) return;
                    setBusy(true);
                    void acceptLaw(session.id)
                      .then(setSession)
                      .catch((ex) => setErr(String(ex)))
                      .finally(() => setBusy(false));
                  }}
                >
                  Commit law
                </button>
                {!canCommitLaw && session?.law_gate?.reasons?.length ? (
                  <p className="meta" style={{ marginTop: "0.5rem" }}>
                    Gates: {session.law_gate.reasons.join("; ")}
                  </p>
                ) : null}
                {session?.status === "accepted" && session.notebook ? (
                  <a
                    className="btn secondary"
                    style={{ marginTop: "0.5rem", display: "inline-block" }}
                    href={notebookDownloadUrl(session.id)}
                    download
                  >
                    Download notebook (.md)
                  </a>
                ) : null}
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
        <LawLibraryPanel />
      </section>
    </main>
  );
}
