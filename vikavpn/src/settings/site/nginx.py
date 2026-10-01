from pathlib import Path

from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class NginxSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="NGINX_")

    available_path: Path = Path("/etc/nginx/sites-available")
    enabled_path: Path = Path("/etc/nginx/sites-enabled")
    service_name: str = "nginx"
