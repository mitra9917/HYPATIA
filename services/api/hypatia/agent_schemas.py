"""JSON Schema exports for Meta Responses contracts (P2.9 / #58, Playbook #38)."""

from __future__ import annotations

from .models import ExperimentProposal, Hypothesis, SceneBrief


def scene_brief_json_schema() -> dict:
    return SceneBrief.model_json_schema()


def hypothesis_batch_json_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "hypotheses": {
                "type": "array",
                "items": Hypothesis.model_json_schema(),
            }
        },
        "required": ["hypotheses"],
    }


def next_test_json_schema() -> dict:
    return ExperimentProposal.model_json_schema()


def exported_schemas() -> dict[str, dict]:
    return {
        "SceneBrief": scene_brief_json_schema(),
        "HypothesisBatch": hypothesis_batch_json_schema(),
        "NextTest": next_test_json_schema(),
    }
