const STORAGE_KEY = "hypatia-recent-sessions";
const ACTIVE_KEY = "hypatia-active-session";
const MAX = 12;

export function getRecentSessionIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    return Array.isArray(parsed) ? parsed.filter((x) => typeof x === "string") : [];
  } catch {
    return [];
  }
}

export function rememberSessionId(id: string): void {
  if (typeof window === "undefined" || !id) return;
  const prev = getRecentSessionIds().filter((x) => x !== id);
  const next = [id, ...prev].slice(0, MAX);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  localStorage.setItem(ACTIVE_KEY, id);
}

export function getActiveSessionId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACTIVE_KEY);
}

export function setActiveSessionId(id: string | null): void {
  if (typeof window === "undefined") return;
  if (id) localStorage.setItem(ACTIVE_KEY, id);
  else localStorage.removeItem(ACTIVE_KEY);
}
