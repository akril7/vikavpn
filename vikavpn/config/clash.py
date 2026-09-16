from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.app import DEFAULT_INSTALL_DIR


class ClashSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CLASH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    configs_store_dir: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "clash" / "configs"
    )
