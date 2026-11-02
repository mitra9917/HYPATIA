from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data"
FIXTURE_DIR = DATA_DIR / "fixtures"
MEDIA_DIR = DATA_DIR / "media"
VIDEO_DIR = DATA_DIR / "videos"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    model_api_key: str = ""
    meta_base_url: str = "https://api.meta.ai/v1"
    meta_observer_model: str = "muse-spark-1.3"
    meta_pi_model: str = "muse-wonder-1.0"
    meta_image_model: str = "muse-image-1.0"
    meta_sam_model: str = "sam-3.1"
    meta_voice_model: str = "muse-voice-transcribe-1.0"
    meta_use_contributor: bool = False

    glimmer_provider: str = "stub"  # modal | baseten | fireworks | stub
    glimmer_baseten_url: str = ""
    glimmer_fireworks_url: str = ""
    baseten_api_key: str = ""
    fireworks_api_key: str = ""

    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket: str = ""
    database_url: str = ""

    fixture_mode: bool = True
    cors_origins: str = "*"
    port: int = 8000

    @property
    def observer_model(self) -> str:
        if self.meta_use_contributor and self.meta_observer_model.startswith("muse-spark"):
            if not self.meta_observer_model.endswith("-contributor"):
                return f"{self.meta_observer_model}-contributor"
        return self.meta_observer_model

    @property
    def has_meta_key(self) -> bool:
        return bool(self.model_api_key.strip())

    @property
    def effective_fixture_mode(self) -> bool:
        # Force fixture when no key; allow explicit fixture even with key.
        if self.fixture_mode:
            return True
        return not self.has_meta_key


@lru_cache
def get_settings() -> Settings:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()
