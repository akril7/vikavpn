from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class NginxSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NGINX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    available_path: Path = Path("/etc/nginx/sites-available")
    enabled_path: Path = Path("/etc/nginx/sites-enabled")
    service_name: str = "nginx"

    def site_available(self, name: str) -> Path:
        return self.available_path / name

    def site_enabled(self, name: str) -> Path:
        return self.enabled_path / name
