from pathlib import Path

from pydantic_settings import BaseSettings

from src.settings.base import make_config


class NginxSettings(BaseSettings):
    model_config = make_config(env_prefix="NGINX_")

    available_path: Path = Path("/etc/nginx/sites-available")
    enabled_path: Path = Path("/etc/nginx/sites-enabled")
    service_name: str = "nginx"
