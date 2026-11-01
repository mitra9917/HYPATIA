"""
HYPATIA on Modal — Meta-named hackathon partner for GPUs, Volumes, Sandboxes.

Deploy:
  modal deploy services/api/modal_app.py

Requires Modal token + secret `hypatia-secrets` with MODEL_API_KEY (and optional AWS_*).
"""

from __future__ import annotations

import modal

app = modal.App("hypatia")

weights = modal.Volume.from_name("hypatia-weights", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install(
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "python-multipart>=0.0.12",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.6.0",
        "httpx>=0.27.0",
        "numpy>=2.1.0",
        "opencv-python-headless>=4.10.0",
        "scipy>=1.14.0",
        "python-dotenv>=1.0.1",
        "aiofiles>=24.1.0",
        "openai>=1.55.0",
        "boto3>=1.35.0",
    )
    .add_local_dir("services/api/hypatia", remote_path="/root/hypatia")
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("hypatia-secrets", required_keys=["MODEL_API_KEY"])],
    volumes={"/weights": weights},
    timeout=60 * 15,
    memory=4096,
)
@modal.asgi_app()
def fastapi_app():
    import sys

    sys.path.insert(0, "/root")
    from hypatia.app import app as api

    return api


@app.function(
    image=image,
    gpu="A10G",
    volumes={"/weights": weights},
    timeout=60 * 20,
    memory=16384,
)
def glimmer_swarm(payload: dict) -> dict:
    """Open-weight hypothesis swarm placeholder — loads weights from Volume when present."""
    # Partner path: swap in real Glimmer serving; stub keeps deploy green.
    n = int(payload.get("n", 32))
    return {
        "provider": "modal",
        "candidates": [
            {"form": "T = 2*pi*sqrt(L/g)", "prior": 0.55},
            {"form": "T = k*L", "prior": 0.25},
            {"form": "T = f(m)", "prior": 0.20},
        ][: max(1, min(n, 3))],
        "weights_mount": "/weights",
    }


@app.function(image=image, timeout=60 * 5, memory=2048)
def toolsmith_run(code: str, test_cmd: str = "python -c 'print(1)'") -> dict:
    """Lightweight stand-in; prefer modal.Sandbox in production Toolsmith."""
    import subprocess
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "tool.py"
        path.write_text(code)
        proc = subprocess.run(test_cmd, shell=True, cwd=td, capture_output=True, text=True, timeout=60)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        }
