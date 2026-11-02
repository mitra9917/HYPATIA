"""Muse Glimmer open-weight swarm — Modal / Baseten / Fireworks / CPU stub (P2.2 / #20)."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .config import Settings

# Pendulum theorist pool — always ≥3 distinct rivals for CI stub / Modal placeholder.
PENDULUM_RIVAL_POOL: list[dict[str, Any]] = [
    {
        "form_id": "pendulum_period",
        "form": "T = 2*pi*sqrt(L/g)",
        "form_latex": r"T = 2\pi\sqrt{L/g}",
        "form_plain": "Small-angle pendulum period",
        "prior": 0.55,
        "source": "stub",
    },
    {
        "form_id": "linear_length",
        "form": "T = k*L",
        "form_latex": r"T = k L",
        "form_plain": "Period proportional to length",
        "prior": 0.25,
        "source": "stub",
    },
    {
        "form_id": "mass_dependent",
        "form": "T = f(m)",
        "form_latex": r"T = f(m)",
        "form_plain": "Period depends on bob mass",
        "prior": 0.15,
        "source": "stub",
    },
    {
        "form_id": "shm_angle",
        "form": "theta(t) = A*cos(sqrt(g/L)*t + phi)",
        "form_latex": r"\theta(t) = A\cos(\sqrt{g/L}\,t + \phi)",
        "form_plain": "SHM angle waveform",
        "prior": 0.12,
        "source": "stub",
    },
    {
        "form_id": "sqrt_length",
        "form": "T = k*sqrt(L)",
        "form_latex": r"T = k\sqrt{L}",
        "form_plain": "Period scales with sqrt length",
        "prior": 0.10,
        "source": "stub",
    },
]

MIN_RIVAL_FORMS = 3


def normalize_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    """Unify partner payloads into theorist card fields."""
    form = str(raw.get("form") or raw.get("form_plain") or "")
    form_id = str(raw.get("form_id") or _infer_form_id(form))
    latex = raw.get("form_latex")
    if not latex:
        latex = _infer_latex(form_id, form)
    plain = raw.get("form_plain") or _infer_plain(form_id, form)
    return {
        "form_id": form_id,
        "form": form or plain,
        "form_latex": latex,
        "form_plain": plain,
        "prior": float(raw.get("prior", 0.1)),
        "source": raw.get("source", "glimmer"),
    }


def _infer_form_id(form: str) -> str:
    f = form.lower().replace(" ", "")
    if "sqrt" in f and "l/g" in f:
        return "pendulum_period"
    if "k*l" in f or "k l" in form.lower():
        return "linear_length"
    if "f(m)" in f:
        return "mass_dependent"
    if "cos" in f:
        return "shm_angle"
    if "sqrt(l)" in f:
        return "sqrt_length"
    return "custom"


def _infer_latex(form_id: str, form: str) -> str:
    for item in PENDULUM_RIVAL_POOL:
        if item["form_id"] == form_id:
            return str(item["form_latex"])
    return form.replace("*", r" \cdot ").replace("pi", r"\pi")


def _infer_plain(form_id: str, form: str) -> str:
    for item in PENDULUM_RIVAL_POOL:
        if item["form_id"] == form_id:
            return str(item["form_plain"])
    return form


def _stub_candidates(*, n: int, domain: str) -> dict[str, Any]:
    k = max(MIN_RIVAL_FORMS, min(n, len(PENDULUM_RIVAL_POOL)))
    candidates = [normalize_candidate(dict(c)) for c in PENDULUM_RIVAL_POOL[:k]]
    return {
        "provider": "stub",
        "domain": domain,
        "candidates": candidates,
        "latency_ms": 0,
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
    out["candidates"] = [normalize_candidate(c) for c in out.get("candidates", [])]
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
    data["candidates"] = [normalize_candidate(c) for c in data.get("candidates", [])]
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


def run_theorist_batch(
    settings: Settings,
    *,
    domain: str = "mechanics.pendulum",
    n: int = 8,
) -> dict[str, Any]:
    """Batch rival functional forms before PySR / held-out scoring."""
    out = run_glimmer_swarm(settings, n=n, domain=domain)
    candidates = out.get("candidates") or []
    if len(candidates) < MIN_RIVAL_FORMS:
        raise RuntimeError(
            f"Glimmer returned {len(candidates)} rivals; need ≥{MIN_RIVAL_FORMS} "
            f"(provider={out.get('provider')})"
        )
    return out


def glimmer_call_log(swarm: dict[str, Any]) -> dict[str, Any]:
    """Structured log row for session.meta_calls (AGENTS.md telemetry)."""
    return {
        "model": "muse-glimmer",
        "provider": swarm.get("provider", "unknown"),
        "ok": True,
        "candidates": len(swarm.get("candidates", [])),
        "latency_ms": int(swarm.get("latency_ms") or 0),
        "domain": swarm.get("domain"),
    }
