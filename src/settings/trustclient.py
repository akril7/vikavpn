from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.app import DEFAULT_INSTALL_DIR
from src.settings.base import make_config


class TrustClientSettings(BaseSettings):
    model_config = make_config(env_prefix="TRUSTCLIENT_")

    # Откуда качаем
    archive_download_link: str = "https://github.com/TrustTunnel/TrustTunnelClient/releases/download/v1.1.11/trusttunnel_client-v1.1.11-linux-x86_64.tar.gz"

    service_name: str = "trustclient-proxy"

    # Папка установки бинарника
    install_dir: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "trustclient"
    )

    # Параметры подключения
    hostname: str = ""
    port: int = 0
    username: str = ""
    password: str = ""

    use_http2_proto: bool = True
    socks5_address: str = "127.0.0.1:1088"
