"""Cell time-lapse domain — logistic growth notebook export (Playbook #54 / issue #36)."""

from __future__ import annotations

from ..models import Session


def cells_logistic_notebook_markdown(session: Session) -> str:
    return "\n".join(
        [
            f"# HYPATIA — cell time-lapse notebook (`{session.id}`)",
            "",
            "**Domain:** biology.cells",
            "",
            "## Accepted growth law (fixture demo)",
            r"$$N(t)=\frac{K}{1+\exp(-r(t-t_0))}$$",
            "",
            "**Interpretation:** colony area / cell count vs time follows logistic saturation.",
            "",
            "| Parameter | Value (demo) |",
            "| --- | --- |",
            "| K (carrying capacity) | 1.0 (normalized) |",
            "| r (growth rate) | 0.42 h⁻¹ |",
            "| doubling time | ~1.65 h |",
            "",
            "_Reuses observe → measure engine; Toolsmith may promote a cell-count tool next._",
        ]
    )
