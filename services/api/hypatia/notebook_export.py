"""Lab notebook markdown export (P2.6 / #24)."""

from __future__ import annotations

from .models import Session


def build_notebook_export(session: Session) -> str:
    nb = session.notebook
    winner = next((h for h in session.hypotheses if h.status == "winner"), None)
    models = sorted({str(c.get("model", "?")) for c in session.meta_calls if c.get("model")})
    csv_path = (
        f"/api/sessions/{session.id}/tracks/0/trajectory.csv" if session.tracks else None
    )
    lines = [
        f"# HYPATIA notebook export — `{session.id}`",
        "",
        f"- **Mode:** {session.mode} · **Source:** {session.source_type}",
        f"- **Upload consent:** {session.upload_consent} ({session.consent_version})",
        "",
    ]
    if nb:
        lines.extend(["## Law", "", nb.markdown or "", ""])
    elif winner:
        lines.extend([f"## Law (pending accept)", "", f"${winner.form_latex}$", ""])
    else:
        lines.append("_No accepted law yet._")
        lines.append("")

    lines.extend(["## Models used", ""])
    if models:
        lines.extend(f"- `{m}`" for m in models)
    else:
        lines.append("- _(none logged)_")
    lines.append("")

    if csv_path:
        lines.extend(["## Measurement", "", f"Trajectory CSV: `{csv_path}`", ""])
    if session.experiment:
        lines.extend(
            [
                "## Recommended experiment",
                "",
                session.experiment.instruction,
                "",
                session.experiment.rationale,
                "",
            ]
        )
    lines.append("---")
    lines.append("_Exported from HYPATIA — LLM proposes, maths decides._")
    return "\n".join(lines)
