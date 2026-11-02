"""ModelRouter — named routes to Meta Model API (P1.2 / Playbook #14)."""

from __future__ import annotations

from typing import Any

from .config import Settings, get_settings
from .contributor_policy import assert_standard_only, observer_spark_model
from .meta_client import MetaClient


class ModelRouter:
    """
    Single entry for hosted Meta calls with consistent logging fields:
    model, kind, latency_ms, optional session_id, token counts when returned.
    """

    def __init__(self, settings: Settings | None = None, *, session_id: str | None = None) -> None:
        self.settings = settings or get_settings()
        assert_standard_only(self.settings.meta_pi_model, "PI")
        assert_standard_only(self.settings.meta_image_model, "Image")
        assert_standard_only(self.settings.meta_sam_model, "SAM")
        self._client = MetaClient(self.settings, session_id=session_id)

    @property
    def client(self) -> MetaClient:
        return self._client

    @property
    def enabled(self) -> bool:
        return self._client.enabled

    def with_session(self, session_id: str) -> ModelRouter:
        return ModelRouter(self.settings, session_id=session_id)

    def health_ping(self) -> dict[str, Any]:
        return self._client.health_ping()

    def observer_json(
        self,
        prompt: str,
        *,
        instructions: str,
        json_schema: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        return self._client.respond_text(
            model=observer_spark_model(self.settings),
            input_payload=prompt,
            instructions=instructions,
            json_schema=json_schema,
        )

    def observe_scene(
        self,
        *,
        prompt: str,
        instructions: str,
        json_schema: dict[str, Any],
        file_id: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Spark Observer with optional uploaded video ``file_id``."""
        if file_id:
            input_payload: list[dict[str, Any]] | str = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_video", "file_id": file_id},
                    ],
                }
            ]
        else:
            input_payload = prompt
        return self._client.respond_text(
            model=observer_spark_model(self.settings),
            input_payload=input_payload,
            instructions=instructions,
            json_schema=json_schema,
        )

    def pi_narrate(self, prompt: str, *, instructions: str) -> tuple[str, dict[str, Any]]:
        return self._client.respond_text(
            model=self.settings.meta_pi_model,
            input_payload=prompt,
            instructions=instructions,
        )

    def sam_probe(self, prompt: str, *, file_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
        return self._client.segment_video_stub_prompt(prompt, file_id=file_id)

    def upload_video_bytes(self, data: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        return self._client.upload_file(data=data, filename=filename, purpose="user_data")

    def generate_image(self, prompt: str) -> tuple[bytes | None, dict[str, Any]]:
        return self._client.generate_image(prompt)
