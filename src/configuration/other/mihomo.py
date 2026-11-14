from pydantic_settings import BaseSettings

from src.configuration.base import make_config


class MihomoSettings(BaseSettings):
    model_config = make_config(env_prefix="MIHOMO_")

    download_url: str = "https://github.com/MetaCubeX/mihomo/releases/download/v1.19.33/mihomo-linux-amd64-v1.19.33.deb"
    service_name: str = "mihomo"

    # Параметры подключения
    hostname: str
    username: str
    password: str
    port: int = 8443
    use_quic: bool = True
    proxy_port: int = 1088
    external_controller_port: int = 10111
    external_controller_secret: str = ""
