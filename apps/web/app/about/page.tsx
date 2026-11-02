import Link from "next/link";
import { PageHeader } from "@/components/shell/PageHeader";

const META_ROWS = [
  { model: "muse-spark-1.3", role: "Observer scene brief", path: "hypatia/observer.py" },
  { model: "sam-3.1", role: "Measure + imagination audit", path: "hypatia/measurer.py" },
  { model: "Muse Glimmer", role: "Hypothesis swarm", path: "hypatia/glimmer.py" },
  { model: "muse-wonder-1.0", role: "PI phase plans", path: "hypatia/pi.py" },
  { model: "muse-image-1.0", role: "Ghost frames", path: "hypatia/pipeline.py" },
  { model: "muse-voice-transcribe-1.0", role: "Voice turn / WebSocket", path: "hypatia/voice.py" },
];

export default function AboutPage() {
  return (
    <>
      <PageHeader
        title="About HYPATIA"
        subtitle="Meta Global AI Developer Hackathon · Indie track · Push the Frontier — the camera that does science."
      />

      <div className="grid two">
        <div className="panel">
          <h2>Scientific loop</h2>
          <p>
            Observe → measure → hypothesize → imagine → experiment → accept. LLM agents plan and narrate; SciPy and
            held-out scores decide which law survives.
          </p>
          <p className="meta">Default path: fixture replay — no Meta API key required for judges.</p>
        </div>
        <div className="panel">
          <h2>Architecture</h2>
          <p>
            Next.js lab UI ↔ FastAPI orchestrator ↔ ModelRouter (Meta Model API) with Modal deploy, optional Postgres,
            and S3 for uploads.
          </p>
          <p className="meta">
            See{" "}
            <a href="https://github.com/mitra9917/HYPATIA/blob/main/docs/ARCHITECTURE.md">ARCHITECTURE.md</a> and{" "}
            <a href="https://github.com/mitra9917/HYPATIA/blob/main/README.md">README</a>.
          </p>
        </div>
      </div>

      <div className="panel">
        <h2>Meta toolkit alignment</h2>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--line)", textAlign: "left" }}>
              <th style={{ padding: "0.5rem 0" }}>Model</th>
              <th>Role</th>
              <th>Module</th>
            </tr>
          </thead>
          <tbody>
            {META_ROWS.map((row) => (
              <tr key={row.model} style={{ borderBottom: "1px solid var(--line)" }}>
                <td style={{ padding: "0.45rem 0" }}>
                  <code>{row.model}</code>
                </td>
                <td>{row.role}</td>
                <td className="meta">{row.path}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="panel">
        <h2>Hackathon & submission</h2>
        <ul>
          <li>
            <a href="https://github.com/mitra9917/HYPATIA/blob/main/docs/HACKATHON_ALIGNMENT.md">HACKATHON_ALIGNMENT</a>{" "}
            — rubric mapping
          </li>
          <li>
            <a href="https://github.com/mitra9917/HYPATIA/blob/main/docs/SUBMISSION_PACK.md">SUBMISSION_PACK</a> — Indie
            one-pager
          </li>
          <li>
            <a href="https://github.com/mitra9917/HYPATIA/blob/main/docs/META_EVIDENCE.md">META_EVIDENCE</a> — judge
            tooling table
          </li>
          <li>
            <a href="https://github.com/mitra9917/HYPATIA/blob/main/docs/EVALS.md">EVALS</a> — fixture eval catalog
          </li>
        </ul>
        <p className="meta">
          Eval summary (fixture): desk-mechanics held-out pass rate 100% — see evals/results/20261102_summary.md
        </p>
      </div>

      <p className="meta">
        UI redesign doc: <Link href="https://github.com/mitra9917/HYPATIA/blob/main/docs/UI_REDESIGN.md">UI_REDESIGN.md</Link>
      </p>
    </>
  );
}
