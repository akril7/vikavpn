from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.app import DEFAULT_INSTALL_DIR


class HysteriaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HYSTERIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = Field(default=11443, ge=1, le=49151)
    mask_url: str = "http://127.0.0.1:7071"
    config_path: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "hysteria" / "hysteria.yaml"
    )

    docker_image_name: str = "teddysun/hysteria"
    docker_container_name: str = "hysteria"
