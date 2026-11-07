from pydantic_settings import BaseSettings

from src.configuration.base import make_config


class ProxySettings(BaseSettings):
    model_config = make_config(env_prefix="PROXY_")

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 1080

    @property
    def address(self) -> str | None:
        return f"{self.host}:{self.port}" if self.enabled else None
