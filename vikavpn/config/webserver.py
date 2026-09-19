from pathlib import Path
from typing import Sequence

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import DEFAULT_INSTALL_DIR, FILES_DIR
from .clash import ClashSettings
from .yoomoney import YoomoneySettings

Mounts = Sequence[tuple[str, str]] | None
ProxyPasses = Sequence[tuple[str, str]] | None


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


# noinspection PyNestedDecorators
class WebServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WEBSERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    title: str = "VIKA-WASSUP"
    ports: list[int] = Field(default_factory=lambda: [443])
    root: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "webserver"
    )

    site_name: str = Field(default="vikavpn-webserver", alias="NGINX_SITE_NAME")

    nginx: NginxSettings = NginxSettings()
    clash: ClashSettings = ClashSettings()
    yoomoney: YoomoneySettings = YoomoneySettings()

    @field_validator("ports")
    @classmethod
    def check_ports(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("ports не может быть пустым")
        if len(set(v)) != len(v):
            raise ValueError("ports содержит дубликаты")
        return v

    @property
    def site_available(self) -> Path:
        return self.nginx.site_available(f"{self.site_name}.conf")

    @property
    def site_enabled(self) -> Path:
        return self.nginx.site_enabled(f"{self.site_name}.conf")

    @property
    def mounts(self) -> Mounts:
        return [
            (self.clash.url_config_path, str(self.clash.configs_store_dir.resolve())),
            ("/files/", str(FILES_DIR))
             ]

    @property
    def proxy_passes(self) -> ProxyPasses:
        return [
            (self.yoomoney.webhook_path, f"http://{self.yoomoney.webhook_host}:{self.yoomoney.webhook_port}")
        ]
