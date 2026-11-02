import {
  PIPELINE_STAGES,
  type PipelineStage,
  type StepperKey,
} from "./pipeline";
import type { HealthInfo, LawSummary, Session, SessionEventPayload } from "./types";

/** In browser, set NEXT_PUBLIC_API_ORIGIN=http://127.0.0.1:8000 to skip Next rewrite (long Meta stages). */
export function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_ORIGIN?.replace(/\/$/, "");
  if (typeof window !== "undefined" && base) {
    return `${base}${path}`;
  }
  return path;
}

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    let message = text.trim() || res.statusText || `HTTP ${res.status}`;
    try {
      const j = JSON.parse(text) as { detail?: unknown };
      if (typeof j.detail === "string") {
        message = j.detail;
      }
    } catch {
      // plain text proxy errors
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function health(): Promise<HealthInfo> {
  return parse(await fetch(apiUrl("/api/health"), { cache: "no-store" }));
}

export type SessionSource = "fixture" | "upload" | "webcam";

export async function createSession(file?: File, source?: SessionSource): Promise<Session> {
  if (!file) {
    const res = await fetch(apiUrl("/api/sessions"), { method: "POST" });
    const data = await parse<{ session: Session }>(res);
    return data.session;
  }
  const body = new FormData();
  body.append("file", file);
  if (source === "webcam" || source === "upload") {
    body.append("source_type", source);
  }
  const res = await fetch(apiUrl("/api/sessions"), { method: "POST", body });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}

export async function getSession(sessionId: string): Promise<Session> {
  return parse(await fetch(apiUrl(`/api/sessions/${sessionId}`), { cache: "no-store" }));
}

export async function runStage(sessionId: string, stage: PipelineStage): Promise<Session> {
  const res = await fetch(apiUrl(`/api/sessions/${sessionId}/${stage}`), { method: "POST" });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}

export async function resumeSession(sessionId: string, fromStage: PipelineStage): Promise<Session> {
  const q = new URLSearchParams({ from_stage: fromStage });
  const res = await fetch(apiUrl(`/api/sessions/${sessionId}/run?${q}`), { method: "POST" });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}

export type StageProgress = {
  stage: PipelineStage;
  phase: "started" | "completed" | "failed";
  session: Session;
};

export async function runSessionWithProgress(
  id: string,
  onProgress?: (progress: StageProgress) => void,
): Promise<Session> {
  let session: Session | null = null;
  for (const stage of PIPELINE_STAGES) {
    onProgress?.({
      stage,
      phase: "started",
      session: session ?? ({ id, status: "created" } as Session),
    });
    session = await runStage(id, stage);
    const phase = session.status === "failed" ? "failed" : "completed";
    onProgress?.({ stage, phase, session });
    if (session.status === "failed") {
      throw new Error(session.error || `Pipeline failed at ${stage}`);
    }
  }
  if (!session) {
    throw new Error("Pipeline produced no session");
  }
  return session;
}

/** @deprecated use runSessionWithProgress */
export async function runSession(id: string): Promise<Session> {
  return runSessionWithProgress(id);
}

export async function observeSession(id: string): Promise<Session> {
  return runStage(id, "observe");
}

export async function fetchTrajectoryCsv(sessionId: string, trackIndex = 0): Promise<string> {
  const res = await fetch(apiUrl(`/api/sessions/${sessionId}/tracks/${trackIndex}/trajectory.csv`));
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.text();
}

export async function listLaws(): Promise<LawSummary[]> {
  const data = await parse<{ laws: LawSummary[] }>(await fetch(apiUrl("/api/library/laws")));
  return data.laws;
}

export type SessionEventHandlers = {
  onSnapshot?: (data: SessionEventPayload) => void;
  onStageStarted?: (data: SessionEventPayload) => void;
  onStageCompleted?: (data: SessionEventPayload) => void;
  onStageFailed?: (data: SessionEventPayload) => void;
  onActiveStep?: (step: StepperKey) => void;
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

/** Subscribe to `GET /api/sessions/{id}/events` (SSE). Returns cleanup. */
export function connectSessionEvents(sessionId: string, handlers: SessionEventHandlers): () => void {
  if (typeof EventSource === "undefined") {
    return () => {};
  }
  const es = new EventSource(apiUrl(`/api/sessions/${sessionId}/events`));

  const bind = (name: string, fn?: (data: SessionEventPayload) => void) => {
    es.addEventListener(name, (ev) => {
      try {
        const data = JSON.parse((ev as MessageEvent).data) as SessionEventPayload;
        fn?.(data);
        if (data.stage && handlers.onActiveStep) {
          handlers.onActiveStep(stageToStep(String(data.stage)));
        }
      } catch {
        // ignore malformed SSE payloads
      }
    });
  };

  bind("snapshot", (data) => {
    handlers.onSnapshot?.(data);
    if (data.status && handlers.onActiveStep) {
      const status = String(data.status);
      const statusStep: Record<string, StepperKey> = {
        created: "created",
        observing: "observe",
        measuring: "measure",
        hypothesizing: "hypothesize",
        imagining: "imagine",
        experimenting: "experiment",
        accepted: "accept",
        failed: "created",
      };
      handlers.onActiveStep(statusStep[status] ?? "created");
    }
  });
  bind("stage_started", handlers.onStageStarted);
  bind("stage_completed", handlers.onStageCompleted);
  bind("stage_failed", handlers.onStageFailed);

  es.onerror = () => {
    // EventSource retries; UI still driven by stage POST responses
  };

  return () => es.close();
}
