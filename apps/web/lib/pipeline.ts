/** Science loop stages — aligned with ARCHITECTURE §4 / API orchestrator. */

export const PIPELINE_STAGES = [
  "observe",
  "measure",
  "hypothesize",
  "imagine",
  "experiment",
  "accept",
] as const;

export type PipelineStage = (typeof PIPELINE_STAGES)[number];

export const STAGE_LABELS: Record<PipelineStage, string> = {
  observe: "Observe",
  measure: "Measure",
  hypothesize: "Hypothesize",
  imagine: "Imagine",
  experiment: "Experiment",
  accept: "Accept",
};

/** UI stepper includes session creation before observe. */
export const STEPPER_KEYS = ["created", ...PIPELINE_STAGES] as const;
export type StepperKey = (typeof STEPPER_KEYS)[number];

export const STEPPER_LABELS: Record<StepperKey, string> = {
  created: "Created",
  ...STAGE_LABELS,
};

const STATUS_TO_STEP: Record<string, StepperKey> = {
  created: "created",
  observing: "observe",
  measuring: "measure",
  hypothesizing: "hypothesize",
  imagining: "imagine",
  experimenting: "experiment",
  accepted: "accept",
  failed: "created",
};

export function statusToActiveStep(status: string): StepperKey {
  if (status === "failed") {
    return "observe";
  }
  return STATUS_TO_STEP[status] ?? "created";
}

export function resolveActiveStep(
  session: Parameters<typeof inferResumeStage>[0] & { status: string },
): StepperKey {
  if (session.status === "failed") {
    return inferResumeStage(session);
  }
  return statusToActiveStep(session.status);
}

export function stepIndex(key: StepperKey): number {
  return STEPPER_KEYS.indexOf(key);
}

export function stageState(
  step: StepperKey,
  active: StepperKey,
  sessionStatus: string,
): "done" | "active" | "pending" | "failed" {
  const si = stepIndex(step);
  const ai = stepIndex(active);
  if (sessionStatus === "failed" && step === active) {
    return "failed";
  }
  if (sessionStatus === "accepted" || si < ai) {
    return "done";
  }
  if (si === ai) {
    return "active";
  }
  return "pending";
}

/** Infer resume stage after failure from session payload. */
export function inferResumeStage(session: { status: string; scene?: unknown; tracks?: unknown[]; hypotheses?: unknown[]; imagination?: unknown[]; experiment?: unknown }): PipelineStage {
  if (session.status !== "failed") {
    return "observe";
  }
  if (!session.scene) return "observe";
  if (!session.tracks?.length) return "measure";
  if (!session.hypotheses?.length) return "hypothesize";
  if (!session.imagination?.length) return "imagine";
  if (!session.experiment) return "experiment";
  return "accept";
}
