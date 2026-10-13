from pydantic_settings import BaseSettings

from src.settings.base import make_config


class ReloaderSettings(BaseSettings):
    model_config = make_config(env_prefix="RELOADER_")

    host: str = "127.0.0.1"
    port: int = 11081

    # debounce/max_delay для Reloader
    debounce: float = 3.0
    max_delay: float = 30.0

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
