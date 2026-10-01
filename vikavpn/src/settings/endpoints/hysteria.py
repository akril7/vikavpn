from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.app import DEFAULT_INSTALL_DIR
from src.settings.base import BaseSettingsConfigDict


class HysteriaSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="HYSTERIA_")

    # Порт для подключения
    port: int = 11443

    # Папка для установки
    install_dir: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "hysteria"
    )

    # Имя файла конфига
    config_name: str = "hysteria.yaml"

    # Docker
    docker_image_name: str = "teddysun/hysteria"
    docker_container_name: str = "hysteria"

    @property
    def config_path(self):
        return self.install_dir / self.config_name
