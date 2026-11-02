import {
  acceptLaw,
  connectSessionEvents,
  createSession,
  getSession,
  runFullSession,
  resumeSession,
  type SessionSource,
} from "@/lib/api";
import type { PipelineStage } from "@/lib/pipeline";
import type { StepperKey } from "@/lib/pipeline";
import type { Session } from "@/lib/types";
import { rememberSessionId } from "@/lib/recent-sessions";

export type LabRunCallbacks = {
  onSession?: (s: Session) => void;
  onActiveStep?: (step: StepperKey) => void;
  onProgress?: (label: string | null) => void;
  onError?: (msg: string) => void;
};

function stageToStep(stage: string): StepperKey {
  const map: Record<string, StepperKey> = {
    observe: "observe",
    measure: "measure",
    hypothesize: "hypothesize",
    imagine: "imagine",
    experiment: "experiment",
    accept: "accept",
  };
  return map[stage] ?? "created";
}

export function attachSessionEvents(sessionId: string, callbacks: LabRunCallbacks): () => void {
  return connectSessionEvents(sessionId, {
    onActiveStep: callbacks.onActiveStep,
    onStageStarted: (d) => callbacks.onProgress?.(d.stage ? `${d.stage}…` : "Running…"),
    onStageCompleted: (d) => {
      callbacks.onProgress?.(null);
      if (d.stage === "observe") {
        void getSession(sessionId).then((s) => callbacks.onSession?.(s)).catch(() => {});
      }
    },
    onStageFailed: (d) =>
      callbacks.onProgress?.(d.error ? String(d.error).slice(0, 80) : "Stage failed"),
  });
}

export async function runFixtureDemo(callbacks: LabRunCallbacks): Promise<Session> {
  callbacks.onProgress?.("Creating session…");
  const created = await createSession();
  rememberSessionId(created.id);
  callbacks.onSession?.(created);
  callbacks.onActiveStep?.("created");
  const disconnect = attachSessionEvents(created.id, callbacks);
  try {
    callbacks.onProgress?.("Running observe → accept…");
    const ran = await runFullSession(created.id);
    rememberSessionId(ran.id);
    callbacks.onSession?.(ran);
    callbacks.onProgress?.(null);
    return ran;
  } finally {
    disconnect();
  }
}

export async function runWithMedia(
  file: File | undefined,
  source: SessionSource,
  uploadConsent: boolean,
  callbacks: LabRunCallbacks,
): Promise<Session> {
  if ((source === "upload" || source === "webcam") && !uploadConsent) {
    throw new Error("Check ethics consent before upload or webcam capture.");
  }
  callbacks.onProgress?.("Creating session…");
  const created = await createSession(
    file,
    source === "webcam" ? "webcam" : source === "upload" ? "upload" : undefined,
    { uploadConsent: source === "fixture" ? true : uploadConsent },
  );
  rememberSessionId(created.id);
  callbacks.onSession?.(created);
  callbacks.onActiveStep?.("created");
  const disconnect = attachSessionEvents(created.id, callbacks);
  try {
    callbacks.onProgress?.("Running observe → accept…");
    const ran = await runFullSession(created.id);
    rememberSessionId(ran.id);
    callbacks.onSession?.(ran);
    callbacks.onProgress?.(null);
    return ran;
  } finally {
    disconnect();
  }
}

export async function resumeFromStage(
  session: Session,
  fromStage: PipelineStage,
  callbacks: LabRunCallbacks,
): Promise<Session> {
  const disconnect = attachSessionEvents(session.id, callbacks);
  try {
    const ran = await resumeSession(session.id, fromStage);
    callbacks.onSession?.(ran);
    if (ran.status === "failed") {
      throw new Error(ran.error || "Resume failed");
    }
    return ran;
  } finally {
    disconnect();
    callbacks.onProgress?.(null);
  }
}

export async function commitLaw(sessionId: string): Promise<Session> {
  const ran = await acceptLaw(sessionId);
  rememberSessionId(ran.id);
  return ran;
}

export function formatRunError(e: unknown): string {
  const msg = e instanceof Error ? e.message : "Run failed";
  if (msg.includes("abort") || msg.includes("AbortError") || msg.includes("timed out")) {
    return "Request timed out — is ./scripts/run_api_local.sh running? Restart API and try again.";
  }
  return msg;
}

export { stageToStep };
