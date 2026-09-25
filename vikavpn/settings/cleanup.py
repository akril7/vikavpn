from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CleanupSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CLEANUP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service: str = Field(default="vikavpn-sub-cleanup", frozen=True)
    hour: int = Field(default=6, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
