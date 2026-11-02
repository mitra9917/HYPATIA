"use client";

import { useCallback, useEffect, useState } from "react";
import { health } from "@/lib/api";
import type { HealthInfo } from "@/lib/types";

export function useHealth(pollMs = 0) {
  const [healthInfo, setHealthInfo] = useState<HealthInfo | null>(null);
  const [healthErr, setHealthErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    void health()
      .then((h) => {
        setHealthInfo(h);
        setHealthErr(null);
      })
      .catch((e) => {
        setHealthInfo({ ok: false });
        setHealthErr(e instanceof Error ? e.message : "API unreachable");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
    if (!pollMs) return;
    const id = window.setInterval(refresh, pollMs);
    return () => window.clearInterval(id);
  }, [refresh, pollMs]);

  return { healthInfo, healthErr, loading, refresh };
}
