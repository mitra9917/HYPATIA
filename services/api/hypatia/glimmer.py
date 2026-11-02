"""Muse Glimmer open-weight swarm — Modal / Baseten / Fireworks / local stub."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .config import Settings


def _stub_candidates(*, n: int, domain: str) -> dict[str, Any]:
    pool = [
        {"form": "T = 2*pi*sqrt(L/g)", "prior": 0.55, "source": "stub"},
        {"form": "T = k*L", "prior": 0.25, "source": "stub"},
        {"form": "T = f(m)", "prior": 0.15, "source": "stub"},
        {"form": "theta(t) = A*cos(sqrt(g/L)*t + phi)", "prior": 0.12, "source": "stub"},
    ]
    k = max(1, min(n, len(pool)))
    return {
        "provider": "stub",
        "domain": domain,
        "candidates": pool[:k],
        "note": "CPU stub for CI/fixture; set GLIMMER_PROVIDER=modal before demo video.",
    }


def _modal_candidates(settings: Settings, *, n: int, domain: str) -> dict[str, Any]:
    """Call deployed Modal function hypatia.glimmer_swarm (GPU path)."""
    import modal

    started = time.time()
    fn = modal.Function.from_name("hypatia", "glimmer_swarm")
    out = fn.remote({"n": n, "domain": domain})
    out["latency_ms"] = int((time.time() - started) * 1000)
    out["provider"] = out.get("provider", "modal")
    return out


def _http_candidates(
    settings: Settings,
    *,
    n: int,
    domain: str,
    provider: str,
    url: str,
    api_key: str,
    header_name: str = "Authorization",
) -> dict[str, Any]:
    started = time.time()
    headers = {header_name: f"Bearer {api_key}"} if api_key else {}
    payload = {"n": n, "domain": domain, "model": "muse-glimmer"}
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    data["provider"] = provider
    data["latency_ms"] = int((time.time() - started) * 1000)
    return data


def run_glimmer_swarm(settings: Settings, *, n: int = 32, domain: str = "mechanics.pendulum") -> dict[str, Any]:
    """Single entry for hypothesis swarm (Playbook #6 / P2.2)."""
    provider = (settings.glimmer_provider or "stub").lower().strip()

    if provider == "stub":
        return _stub_candidates(n=n, domain=domain)

    if provider == "modal":
        return _modal_candidates(settings, n=n, domain=domain)

    if provider == "baseten":
        url = settings.glimmer_baseten_url.strip()
        if not url or not settings.baseten_api_key.strip():
            raise RuntimeError("GLIMMER_PROVIDER=baseten requires BASETEN_API_KEY and GLIMMER_BASETEN_URL")
        return _http_candidates(
            settings,
            n=n,
            domain=domain,
            provider="baseten",
            url=url,
            api_key=settings.baseten_api_key,
        )

    if provider == "fireworks":
        url = settings.glimmer_fireworks_url.strip() or "https://api.fireworks.ai/inference/v1/completions"
        if not settings.fireworks_api_key.strip():
            raise RuntimeError("GLIMMER_PROVIDER=fireworks requires FIREWORKS_API_KEY")
        return _http_candidates(
            settings,
            n=n,
            domain=domain,
            provider="fireworks",
            url=url,
            api_key=settings.fireworks_api_key,
        )

    raise ValueError(f"Unknown GLIMMER_PROVIDER={provider!r} (use stub|modal|baseten|fireworks)")
