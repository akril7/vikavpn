from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.app import DEFAULT_INSTALL_DIR
from src.settings.base import BaseSettingsConfigDict


class SiteSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="SITE_")

    # Заголовок для страницы-заглушки
    title: str = "VIKA-WASSUP"

    # Порт для сайта
    port: int = 7071

    # Дополнительные порты для сайта
    extra_ports: list[int] = Field(default_factory=lambda: [443])

    # root папка сайта
    root_dir: Path = Field(default_factory=lambda: DEFAULT_INSTALL_DIR / "site")

    # имя файла для конфига сайта
    name: str = "vikavpn-site"
