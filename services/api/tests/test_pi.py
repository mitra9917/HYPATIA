"""Wonder PI orchestration tests (P2.3 / Playbook #31 / #21)."""

from __future__ import annotations

import asyncio
import json
import os

os.environ.setdefault("FIXTURE_MODE", "true")
os.environ.setdefault("MODEL_API_KEY", "")

from hypatia.config import Settings, get_settings  # noqa: E402
from hypatia.models import Session, SessionStatus  # noqa: E402
from hypatia.pi import PI_PHASES, fixture_pi_plan, plan_pi_phase, wonder_plan_calls  # noqa: E402

get_settings.cache_clear()


def test_fixture_pi_plan_once_per_phase() -> None:
    session = Session(id="s1", status=SessionStatus.created, mode="fixture")
    settings = Settings()

    class FakeClient:
        enabled = False

    client = FakeClient()
    for phase in PI_PHASES:
        p1 = asyncio.run(plan_pi_phase(session, client, settings, phase))  # type: ignore[arg-type]
        p2 = asyncio.run(plan_pi_phase(session, client, settings, phase))  # type: ignore[arg-type]
        assert p1 == p2
        assert phase in session.pi_plans
        assert len(p1.get("tools", [])) >= 1


def test_fixture_hypothesize_plan_includes_theorist_tools() -> None:
    session = Session(id="s2", mode="fixture")
    plan = fixture_pi_plan("hypothesize", session)
    assert "spawn_theorist" in plan["tools"]
    assert "run_pysr" in plan["tools"]


def test_live_pi_uses_previous_response_id() -> None:
    session = Session(id="s3", mode="live")
    settings = Settings(model_api_key="test-key", meta_pi_model="muse-wonder-1.0")
    calls: list[dict] = []

    class FakeClient:
        enabled = True

        def respond_text(self, **kwargs):  # noqa: ANN003
            calls.append(kwargs)
            phase = "observe" if len(calls) == 1 else "measure"
            body = fixture_pi_plan(phase, session)
            rid = f"resp_{len(calls)}"
            return json.dumps(body), {
                "ok": True,
                "model": settings.meta_pi_model,
                "response_id": rid,
                "role": "pi_plan",
            }

    client = FakeClient()
    asyncio.run(plan_pi_phase(session, client, settings, "observe"))  # type: ignore[arg-type]
    asyncio.run(plan_pi_phase(session, client, settings, "measure"))  # type: ignore[arg-type]
    assert calls[0].get("previous_response_id") is None
    assert calls[1].get("previous_response_id") == "resp_1"
    assert session.pi_response_id == "resp_2"
    assert wonder_plan_calls(session, pi_model=settings.meta_pi_model) == 2
