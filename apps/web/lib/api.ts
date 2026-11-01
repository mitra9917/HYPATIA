import type { Session } from "./types";

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function health(): Promise<Record<string, unknown>> {
  return parse(await fetch("/api/health", { cache: "no-store" }));
}

export async function createSession(file?: File): Promise<Session> {
  const body = new FormData();
  if (file) body.append("file", file);
  const res = await fetch("/api/sessions", { method: "POST", body: file ? body : undefined });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}

export async function runSession(id: string): Promise<Session> {
  const res = await fetch(`/api/sessions/${id}/run`, { method: "POST" });
  const data = await parse<{ session: Session }>(res);
  return data.session;
}
