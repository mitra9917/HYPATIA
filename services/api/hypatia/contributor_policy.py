"""Spark Contributor routing policy (P1.14 / Playbook #27, issue #54)."""

from __future__ import annotations

from .config import Settings

CONTRIBUTOR_SUFFIX = "-contributor"
SPARK_PREFIX = "muse-spark"


def observer_spark_model(settings: Settings) -> str:
    """Only Observer / cheap Spark loops may use Contributor variant."""
    return settings.observer_model


def spark_routing_tier(model_id: str) -> str | None:
    """Return contributor | standard for Spark models; None for non-Spark."""
    if not model_id.startswith(SPARK_PREFIX):
        return None
    return "contributor" if model_id.endswith(CONTRIBUTOR_SUFFIX) else "standard"


def assert_standard_only(model_id: str, role: str) -> None:
    """Wonder / Image / SAM must never use Contributor IDs."""
    if CONTRIBUTOR_SUFFIX in model_id:
        raise ValueError(f"{role} must not use Contributor model id: {model_id}")


def contributor_policy_summary(settings: Settings) -> dict[str, str | bool]:
    obs = observer_spark_model(settings)
    tier = spark_routing_tier(obs) or "standard"
    return {
        "meta_use_contributor": settings.meta_use_contributor,
        "observer_spark_tier": tier,
        "observer_model": obs,
        "pi_model": settings.meta_pi_model,
        "image_model": settings.meta_image_model,
        "sam_model": settings.meta_sam_model,
        "policy": "Contributor applies to Observer Spark only; Wonder, Image, and SAM stay standard.",
    }
