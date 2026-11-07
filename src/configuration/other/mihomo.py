from pydantic_settings import BaseSettings

from src.configuration.base import make_config


class MihomoSettings(BaseSettings):
    model_config = make_config(env_prefix="MIHOMO_")

    download_url: str = "https://github.com/MetaCubeX/mihomo/releases/download/v1.19.33/mihomo-linux-amd64-v1.19.33.deb"
    service_name: str = "mihomo"

    # Параметры подключения
    hostname: str = ""
    port: int = 8443
    username: str = ""
    password: str = ""
    use_quic: bool = True
    proxy_port: int = 1088
