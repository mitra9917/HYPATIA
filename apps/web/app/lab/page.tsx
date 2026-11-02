"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { AcceptGatePanel } from "@/components/AcceptGatePanel";
import { EthicsConsentBanner } from "@/components/EthicsConsentBanner";
import { HypothesisCard } from "@/components/HypothesisCard";
import { HypothesisLeaderboard } from "@/components/HypothesisLeaderboard";
import { ObserverNarration } from "@/components/ObserverNarration";
import { PipelineStepper } from "@/components/PipelineStepper";
import { SessionErrorPanel } from "@/components/SessionErrorPanel";
import { PageHeader } from "@/components/shell/PageHeader";
import { TrackOverlay } from "@/components/TrackOverlay";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import { WebcamCapture } from "@/components/WebcamCapture";
import { submitExperimentResult, getSession } from "@/lib/api";
import { formatRunError, resumeFromStage, runFixtureDemo, runWithMedia } from "@/lib/lab-run";
import type { PipelineStage } from "@/lib/pipeline";
import type { StepperKey } from "@/lib/pipeline";
import type { Hypothesis, Session } from "@/lib/types";
import { rememberSessionId } from "@/lib/recent-sessions";
import { useHealth } from "@/lib/use-health";

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

function LabPageInner() {
  const router = useRouter();
  const params = useSearchParams();
  const { healthInfo } = useHealth();
  const [session, setSession] = useState<Session | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<StepperKey>("created");
  const [progressLabel, setProgressLabel] = useState<string | null>(null);
  const [uploadConsent, setUploadConsent] = useState(false);
  const [demoStarted, setDemoStarted] = useState(false);

  const callbacks = useMemo(
    () => ({
      onSession: setSession,
      onActiveStep: setActiveStep,
      onProgress: setProgressLabel,
    }),
    [],
  );

  async function onRun(file?: File, source: "upload" | "webcam" | "fixture" = "fixture") {
    setBusy(true);
    setErr(null);
    try {
      const ran =
        source === "fixture" && !file
          ? await runFixtureDemo(callbacks)
          : await runWithMedia(file, source, uploadConsent, callbacks);
      rememberSessionId(ran.id);
      router.push(`/session/${ran.id}`);
    } catch (e) {
      setErr(formatRunError(e));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    const sid = params.get("session");
    if (sid) {
      void getSession(sid)
        .then((s) => {
          setSession(s);
          rememberSessionId(s.id);
        })
        .catch(() => {});
    }
  }, [params]);

  useEffect(() => {
    if (params.get("demo") !== "1" || demoStarted || busy || params.get("session")) return;
    setDemoStarted(true);
    void onRun(undefined, "fixture");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params, demoStarted, busy]);

  async function onResume(fromStage: PipelineStage) {
    if (!session) return;
    setBusy(true);
    setErr(null);
    try {
      await resumeFromStage(session, fromStage, callbacks);
    } catch (e) {
      setErr(formatRunError(e));
    } finally {
      setBusy(false);
    }
  }

  const showStepper = Boolean(session) || busy;

  return (
    <>
      <PageHeader
        title="Lab"
        subtitle="Live capture or fixture replay through the full scientific loop. Progress streams over SSE while stages run."
        actions={
          <button type="button" className="btn" disabled={busy} onClick={() => void onRun(undefined, "fixture")}>
            {busy ? progressLabel || "Running…" : "Run desk pendulum demo"}
          </button>
        }
      />

      {err ? (
        <SessionErrorPanel
          message={err}
          session={session}
          busy={busy}
          onResume={session?.status === "failed" ? onResume : undefined}
        />
      ) : null}

      {busy && progressLabel ? (
        <p className="meta" style={{ marginBottom: "1rem" }} aria-live="polite">
          {progressLabel}
        </p>
      ) : null}

      <div className="panel panel--flat" style={{ marginBottom: "1rem" }}>
        <EthicsConsentBanner checked={uploadConsent} onChange={setUploadConsent} />
        <div className="page-header__actions" style={{ marginTop: "1rem" }}>
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
        <p className="meta" style={{ marginTop: "0.75rem" }}>
          Webcam burst length is adjustable (5–15s). Requires consent for upload/webcam.
        </p>
      </div>

      {showStepper && session ? <PipelineStepper session={session} activeStep={activeStep} busy={busy} /> : null}

      {session?.library_hint ? (
        <p className="meta" style={{ marginBottom: "1rem" }}>
          {session.library_hint.message}
        </p>
      ) : null}

      <div className="grid two">
        <div className="panel">
          <h2>Observe</h2>
          {session ? (
            <>
              <ObserverNarration
                narration={session.scene?.narration ?? ""}
                domain={session.scene?.suggested_domain}
                placeholder="Spark Observer narrates after the watch step…"
              />
              {session.scene?.sam_prompts?.length ? (
                <div style={{ marginTop: "0.75rem" }}>
                  {session.scene.sam_prompts.map((p) => (
                    <span key={p} className="pill">
                      {p}
                    </span>
                  ))}
                </div>
              ) : null}
            </>
          ) : (
            <p className="meta">Start a session to see Muse Spark scene brief and SAM prompts.</p>
          )}
        </div>
        <div className="panel">
          <h2>Measure</h2>
          {session?.tracks?.length ? (
            <>
              <TrackOverlay tracks={session.tracks} />
              <TrajectoryChart points={session.tracks[0]?.points} title="Pendulum angle vs time" />
            </>
          ) : (
            <p className="meta">SAM 3.1 mask scrubber and trajectory chart appear after measure.</p>
          )}
        </div>
      </div>

      <div className="grid two">
        <div className="panel">
          <h2>Rival theories</h2>
          <HypothesisLeaderboard hypotheses={session?.hypotheses ?? []} />
          <div className="cards" style={{ marginTop: "1rem" }}>
            {(session?.hypotheses ?? []).map((h) => (
              <HypothesisCard key={h.id} hypothesis={h} demoLine={demoGLine(h)} />
            ))}
          </div>
        </div>
        <div className="panel">
          <h2>Accept gate</h2>
          <AcceptGatePanel session={session} />
        </div>
      </div>

      {session ? (
        <p className="meta">
          Session <code>{session.id.slice(0, 8)}</code> · mode {session.mode} ·{" "}
          {healthInfo?.fixture_mode ? "fixture replay" : "live paths"} ·{" "}
          <Link href={`/session/${session.id}`}>Open session detail →</Link>
        </p>
      ) : null}

      {session?.experiment && !session.experiment_result ? (
        <div className="panel">
          <h2>Log experiment result</h2>
          <form
            className="meta"
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
              Period ratio{" "}
              <input name="ratio" type="number" step="0.01" defaultValue="1.41" />
            </label>
            <input name="notes" type="text" placeholder="Notes" style={{ marginLeft: "0.5rem" }} />
            <button type="submit" className="btn secondary" style={{ marginLeft: "0.5rem" }}>
              Submit
            </button>
          </form>
        </div>
      ) : null}
    </>
  );
}

export default function LabPage() {
  return (
    <Suspense fallback={<p className="meta">Loading lab…</p>}>
      <LabPageInner />
    </Suspense>
  );
}
