import type { Session } from "./types";

/** In browser, set NEXT_PUBLIC_API_ORIGIN=http://127.0.0.1:8000 to skip Next rewrite (long Meta stages). */
function apiUrl(path: string): string {
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
      // e.g. plain "Internal Server Error" from proxy — not JSON
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function health(): Promise<Record<string, unknown>> {
  return parse(await fetch(apiUrl("/api/health"), { cache: "no-store" }));
}

export async function createSession(file?: File): Promise<Session> {
  const body = new FormData();
  if (file) body.append("file", file);
  const res = await fetch(apiUrl("/api/sessions"), { method: "POST", body: file ? body : undefined });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}

const PIPELINE_STAGES = [
  "observe",
  "measure",
  "hypothesize",
  "imagine",
  "experiment",
  "accept",
] as const;

export async function runSession(id: string): Promise<Session> {
  // Stage-by-stage avoids long single /run proxy timeouts in local dev (Meta calls can take minutes).
  let session: Session | null = null;
  for (const stage of PIPELINE_STAGES) {
    const res = await fetch(apiUrl(`/api/sessions/${id}/${stage}`), { method: "POST" });
    const data = await parse<{ session: Session }>(res);
    session = data.session;
    if (session.status === "failed") {
      throw new Error(session.error || `Pipeline failed at ${stage}`);
    }
  }
  if (!session) {
    throw new Error("Pipeline produced no session");
  }
  return session;
}

export async function observeSession(id: string): Promise<Session> {
  const res = await fetch(apiUrl(`/api/sessions/${id}/observe`), { method: "POST" });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}
