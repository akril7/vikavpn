from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.app import DEFAULT_INSTALL_DIR
from src.settings.base import make_config


class HysteriaSettings(BaseSettings):
    model_config = make_config(env_prefix="HYSTERIA_")

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

    # Имя сервиса
    service_name: str = "vikavpn-hysteria"

    # Хост для auth сервиса
    auth_host: str = "127.0.0.1"

    # Порт для auth сервиса
    auth_port: int = 11080

    # Path для auth сервиса
    auth_path: str = "/auth"

    @property
    def config_path(self):
        return self.install_dir / self.config_name

    @property
    def auth_url(self) -> str:
        return f"http://{self.auth_host}:{self.auth_port}{self.auth_path}"
