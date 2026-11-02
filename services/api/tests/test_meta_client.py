"""P1.2 Meta client / ModelRouter unit tests (no live API)."""

from __future__ import annotations

import os

import pytest

os.environ["MODEL_API_KEY"] = "LLM_test_key_do_not_log"
os.environ["FIXTURE_MODE"] = "true"

from hypatia.config import Settings, get_settings  # noqa: E402
from hypatia.meta_client import MetaClient  # noqa: E402
from hypatia.model_router import ModelRouter  # noqa: E402

get_settings.cache_clear()


def test_log_includes_session_id_and_never_raw_key() -> None:
    client = MetaClient(Settings(model_api_key="LLM_test_key_do_not_log"), session_id="sess-abc")
    log = client._log("muse-spark-1.3", "responses", started=0.0, extra={"ok": True})
    assert log["session_id"] == "sess-abc"
    assert log["model"] == "muse-spark-1.3"
    assert "LLM_test" not in str(log)
    assert "model_api_key" not in log


def test_contributor_routing_on_observer() -> None:
    s = Settings(model_api_key="x", meta_use_contributor=True)
    assert s.observer_model == "muse-spark-1.3-contributor"


def test_model_router_delegates_enabled() -> None:
    router = ModelRouter(Settings(model_api_key=""))
    assert router.enabled is False
    router2 = ModelRouter(Settings(model_api_key="LLM_x"))
    assert router2.enabled is True
    assert router2.with_session("s1").client.session_id == "s1"
