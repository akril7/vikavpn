from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.app import DEFAULT_INSTALL_DIR
from src.settings.base import BaseSettingsConfigDict


class ClashSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="CLASH_")

    # Папка, где хранить clash-конфиги пользователей
    configs_store_dir: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "clash" / "configs"
    )

    # URL путь для получения clash-конфига
    configs_urlpath: str = "/sub/"
