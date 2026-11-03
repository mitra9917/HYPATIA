"""Runtime ops mode override — flip fixture/live/hybrid without redeploy (P3.8 / #33)."""

from __future__ import annotations

from enum import Enum

from .config import Settings


class OpsMode(str, Enum):
    fixture = "fixture"
    live = "live"
    hybrid = "hybrid"


_override: OpsMode | None = None


def get_ops_mode_override() -> OpsMode | None:
    return _override


def set_ops_mode(mode: OpsMode | None) -> OpsMode | None:
    global _override
    _override = mode
    return _override


def resolve_ops_mode(settings: Settings) -> OpsMode:
    if _override is not None:
        return _override
    if settings.fixture_mode or not settings.has_meta_key:
        return OpsMode.fixture
    return OpsMode.live


def resolve_fixture_mode(settings: Settings) -> bool:
    """True → repo fixtures / replay; False → attempt live Meta paths."""
    mode = resolve_ops_mode(settings)
    if mode == OpsMode.fixture:
        return True
    if mode in (OpsMode.live, OpsMode.hybrid):
        return not settings.has_meta_key
    return settings.effective_fixture_mode


def ops_mode_summary(settings: Settings) -> dict[str, object]:
    mode = resolve_ops_mode(settings)
    return {
        "ops_mode": mode.value,
        "ops_mode_override": _override.value if _override else None,
        "fixture_mode": resolve_fixture_mode(settings),
        "hybrid_fallback_enabled": mode == OpsMode.hybrid,
        "meta_key_present": settings.has_meta_key,
        "locked": settings.ops_mode_locked,
    }
