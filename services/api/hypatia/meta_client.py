"""
Meta Model API client — Responses, Files, Images, SAM probes.

Environment (see repo `.env.example`):
  MODEL_API_KEY          Bearer token (never log this value)
  META_BASE_URL          Default https://api.meta.ai/v1
  META_OBSERVER_MODEL    muse-spark-1.3 (+ -contributor when META_USE_CONTRIBUTOR=true)
  META_PI_MODEL          muse-wonder-1.0
  META_IMAGE_MODEL       muse-image-1.0
  META_SAM_MODEL         sam-3.1
  META_VOICE_MODEL       muse-voice-transcribe-1.0
"""

from __future__ import annotations

import base64
import io
import json
import logging
import time
from typing import Any

from openai import OpenAI

from .config import Settings
from .contributor_policy import spark_routing_tier

logger = logging.getLogger(__name__)


class MetaClient:
    """Thin wrapper around Meta Model API (OpenAI-compatible Responses + helpers)."""

    def __init__(self, settings: Settings, *, session_id: str | None = None) -> None:
        self.settings = settings
        self.session_id = session_id
        self._client: OpenAI | None = None
        if settings.has_meta_key:
            self._client = OpenAI(
                api_key=settings.model_api_key,
                base_url=settings.meta_base_url,
            )

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def with_session(self, session_id: str) -> MetaClient:
        return MetaClient(self.settings, session_id=session_id)

    def _log(
        self,
        model: str,
        kind: str,
        started: float,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "kind": kind,
            "latency_ms": int((time.time() - started) * 1000),
        }
        if self.session_id:
            payload["session_id"] = self.session_id
        if extra:
            payload.update(extra)
        tier = spark_routing_tier(model)
        if tier:
            payload["spark_routing"] = tier
            logger.info(
                "meta_spark_call model=%s spark_routing=%s kind=%s session_id=%s",
                model,
                tier,
                kind,
                self.session_id or "-",
            )
        return payload

    @staticmethod
    def _usage_fields(resp: Any) -> dict[str, int]:
        usage = getattr(resp, "usage", None)
        if not usage:
            return {}
        out: dict[str, int] = {}
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            val = getattr(usage, key, None)
            if val is not None:
                out[key] = int(val)
        return out

    def respond_text(
        self,
        *,
        model: str,
        input_payload: list[dict[str, Any]] | str,
        instructions: str | None = None,
        json_schema: dict[str, Any] | None = None,
        previous_response_id: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        if not self._client:
            raise RuntimeError("MODEL_API_KEY not set")
        started = time.time()
        kwargs: dict[str, Any] = {
            "model": model,
            "input": input_payload,
        }
        if instructions:
            kwargs["instructions"] = instructions
        if previous_response_id:
            kwargs["previous_response_id"] = previous_response_id
        if json_schema:
            kwargs["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": json_schema.get("name", "result"),
                    "schema": json_schema.get("schema", json_schema),
                    "strict": True,
                }
            }
        try:
            resp = self._client.responses.create(**kwargs)
            text = getattr(resp, "output_text", None) or _extract_output_text(resp)
            log = self._log(
                model,
                "responses",
                started,
                {
                    "ok": True,
                    "response_id": getattr(resp, "id", None),
                    **self._usage_fields(resp),
                },
            )
            return text, log
        except Exception as exc:  # noqa: BLE001
            try:
                messages = []
                if instructions:
                    messages.append({"role": "system", "content": instructions})
                if isinstance(input_payload, str):
                    messages.append({"role": "user", "content": input_payload})
                else:
                    messages.append({"role": "user", "content": json.dumps(input_payload)})
                chat = self._client.chat.completions.create(model=model, messages=messages)
                text = chat.choices[0].message.content or ""
                log = self._log(
                    model,
                    "chat.completions_fallback",
                    started,
                    {"ok": True, "note": str(exc)[:120], **self._usage_fields(chat)},
                )
                return text, log
            except Exception as exc2:  # noqa: BLE001
                log = self._log(model, "responses", started, {"ok": False, "error": str(exc2)[:200]})
                raise RuntimeError(f"Meta API call failed: {exc2}") from exc2

    def upload_file(
        self,
        *,
        data: bytes,
        filename: str,
        purpose: str = "user_data",
    ) -> tuple[str, dict[str, Any]]:
        """Upload bytes via Files API; returns Meta `file_id` for video/image reuse."""
        if not self._client:
            raise RuntimeError("MODEL_API_KEY not set")
        started = time.time()
        try:
            buf = io.BytesIO(data)
            buf.name = filename
            created = self._client.files.create(file=buf, purpose=purpose)
            file_id = str(created.id)
            log = self._log(
                "files",
                "files.create",
                started,
                {"ok": True, "file_id": file_id, "bytes": len(data), "purpose": purpose},
            )
            return file_id, log
        except Exception as exc:  # noqa: BLE001
            log = self._log("files", "files.create", started, {"ok": False, "error": str(exc)[:200]})
            raise RuntimeError(f"Meta Files API upload failed: {exc}") from exc

    def segment_video_stub_prompt(self, prompt: str, file_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
        """Non-streaming SAM fallback when streaming path unavailable."""
        if not self._client:
            raise RuntimeError("MODEL_API_KEY not set")
        if not file_id:
            raise RuntimeError("SAM 3 video requires input_video file_id")
        started = time.time()
        content: list[dict[str, Any]] = [
            {"type": "input_video", "file_id": file_id},
            {"type": "input_text", "text": prompt},
        ]
        try:
            resp = self._client.responses.create(
                model=self.settings.meta_sam_model,
                input=[{"role": "user", "content": content}],
            )
            text = getattr(resp, "output_text", None) or _extract_output_text(resp)
            log = self._log(
                self.settings.meta_sam_model,
                "sam",
                started,
                {"ok": True, "chars": len(text), "file_id": file_id, **self._usage_fields(resp)},
            )
            return {"raw": text}, log
        except Exception as exc:  # noqa: BLE001
            log = self._log(
                self.settings.meta_sam_model,
                "sam",
                started,
                {"ok": False, "error": str(exc)[:200], "file_id": file_id},
            )
            raise RuntimeError(str(exc)) from exc

    async def segment_video_tracked(
        self,
        prompt: str,
        *,
        file_id: str,
        media_size: tuple[int, int],
    ) -> tuple[list[Any], dict[str, Any]]:
        """Stream SAM 3.1 video + meta_sam_parser decode (Playbook #19)."""
        if not self._client:
            raise RuntimeError("MODEL_API_KEY not set")
        from .sam_live import segment_video_async

        try:
            masks, log = await segment_video_async(
                self._client,
                self.settings,
                prompt=prompt,
                file_id=file_id,
                media_size=media_size,
                session_id=self.session_id,
            )
            return masks, log
        except Exception as exc:  # noqa: BLE001
            started = time.time()
            log = self._log(
                self.settings.meta_sam_model,
                "sam",
                started,
                {"ok": False, "error": str(exc)[:200], "file_id": file_id, "stream": True},
            )
            raise

    def generate_image(self, prompt: str) -> tuple[bytes | None, dict[str, Any]]:
        if not self._client:
            raise RuntimeError("MODEL_API_KEY not set")
        started = time.time()
        try:
            img = self._client.images.generate(
                model=self.settings.meta_image_model,
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
            b64 = img.data[0].b64_json if img.data else None
            raw = base64.b64decode(b64) if b64 else None
            log = self._log(self.settings.meta_image_model, "images.generate", started, {"ok": True})
            log["images_generated"] = 1
            log["image_spend_usd_est"] = 0.01
            return raw, log
        except Exception as exc:  # noqa: BLE001
            log = self._log(
                self.settings.meta_image_model,
                "images.generate",
                started,
                {"ok": False, "error": str(exc)[:200]},
            )
            raise

    def health_ping(self) -> dict[str, Any]:
        if not self.enabled:
            return {"meta": False, "reason": "no MODEL_API_KEY"}
        started = time.time()
        try:
            text, log = self.respond_text(
                model=self.settings.observer_model,
                input_payload="Reply with the single word: pong",
                instructions="You are a health check. Reply only pong.",
            )
            return {
                "meta": True,
                "pong": text.strip()[:32],
                "latency_ms": log.get("latency_ms", int((time.time() - started) * 1000)),
                "model": log.get("model"),
            }
        except Exception as exc:  # noqa: BLE001
            return {"meta": False, "error": str(exc)[:200]}


def _extract_output_text(resp: Any) -> str:
    try:
        chunks: list[str] = []
        for item in getattr(resp, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                t = getattr(c, "text", None)
                if t:
                    chunks.append(t)
        return "\n".join(chunks)
    except Exception:  # noqa: BLE001
        return ""


async def upload_bytes_to_s3(settings: Settings, key: str, data: bytes, content_type: str = "application/octet-stream") -> str | None:
    if not settings.s3_bucket or not settings.aws_access_key_id:
        return None
    import boto3

    client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    client.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)
    return f"s3://{settings.s3_bucket}/{key}"
