"use client";

import { inferResumeStage, STAGE_LABELS, type PipelineStage } from "@/lib/pipeline";
import type { Session } from "@/lib/types";

type Props = {
  message: string;
  session: Session | null;
  onResume?: (fromStage: PipelineStage) => void;
  busy?: boolean;
};

export function SessionErrorPanel({ message, session, onResume, busy }: Props) {
  const resumeStage = session ? inferResumeStage(session) : "observe";

  return (
    <div className="panel session-error" role="alert">
      <strong>Stage failed</strong>
      <pre className="meta">{message}</pre>
      <p className="meta retry-hint">
        Per demo runbook: switch to hybrid/fixture if Meta is slow, or retry the failed stage. On
        camera, prefer fixture replay over debugging API errors.
      </p>
      {session && onResume ? (
        <button
          type="button"
          className="btn secondary"
          disabled={busy}
          onClick={() => onResume(resumeStage)}
        >
          Resume from {STAGE_LABELS[resumeStage]}
        </button>
      ) : null}
    </div>
  );
}
