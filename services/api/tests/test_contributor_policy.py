"""Contributor routing policy tests (P1.14 / #54)."""

from __future__ import annotations

import pytest

from hypatia.config import Settings
from hypatia.contributor_policy import (
    assert_standard_only,
    contributor_policy_summary,
    observer_spark_model,
    spark_routing_tier,
)
from hypatia.meta_client import MetaClient
from hypatia.model_router import ModelRouter


def test_observer_spark_contributor_suffix() -> None:
    s = Settings(model_api_key="x", meta_use_contributor=True)
    assert observer_spark_model(s) == "muse-spark-1.3-contributor"
    assert spark_routing_tier(observer_spark_model(s)) == "contributor"


def test_observer_spark_standard_by_default() -> None:
    s = Settings(model_api_key="x", meta_use_contributor=False)
    assert spark_routing_tier(observer_spark_model(s)) == "standard"


def test_wonder_image_sam_reject_contributor_ids() -> None:
    with pytest.raises(ValueError, match="PI"):
        assert_standard_only("muse-wonder-1.0-contributor", "PI")
    with pytest.raises(ValueError, match="SAM"):
        assert_standard_only("sam-3.1-contributor", "SAM")


def test_model_router_blocks_bad_sam_config() -> None:
    with pytest.raises(ValueError):
        ModelRouter(Settings(model_api_key="x", meta_sam_model="sam-3.1-contributor"))


def test_spark_log_includes_routing_tier() -> None:
    client = MetaClient(Settings(model_api_key="x"), session_id="s1")
    log = client._log("muse-spark-1.3-contributor", "responses", started=0.0, extra={"ok": True})
    assert log["spark_routing"] == "contributor"


def test_health_policy_summary() -> None:
    summary = contributor_policy_summary(Settings(meta_use_contributor=True, model_api_key="x"))
    assert summary["observer_spark_tier"] == "contributor"
    assert summary["meta_use_contributor"] is True
    assert "sam-3.1" in str(summary["sam_model"])
