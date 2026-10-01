from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.app import DEFAULT_INSTALL_DIR
from src.settings.base import BaseSettingsConfigDict


class TrustTunnelSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="TRUSTTUNNEL_")

    # Порт для подключения
    port: int = 8443

    # Разрешенные SNI для подключения
    sni: str = "apple.com"

    # Имя сервиса
    service_name: str = "vikavpn-trusttunnel"

    # Папка установки бинарника
    install_dir: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "trusttunnel"
    )

    # Ссылка для скачивания архива с бинарником
    archive_download_link: str = (
        "https://github.com/akril7/TrustTunnel/releases/download/0.0.0/trusttunnel-patched-v1.1.0-linux-x86_64.tar.gz"
    )
