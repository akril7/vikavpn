from pathlib import Path
from typing import Sequence

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import DEFAULT_INSTALL_DIR, FILES_DIR
from .clash import ClashSettings
from .nginx import NginxSettings

Mounts = Sequence[tuple[str, str]] | None


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

    @field_validator("ports", mode="before")
    @classmethod
    def parse_ports(cls, v):
        if isinstance(v, str):
            return [int(p.strip()) for p in v.split(",") if p.strip()]
        return v

    @field_validator("ports")
    @classmethod
    def check_ports(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("ports не может быть пустым")
        for p in v:
            if not (1 <= p <= 49151):
                raise ValueError(f"порт {p} вне диапазона 1–49151")
        if len(set(v)) != len(v):
            raise ValueError("ports содержит дубликаты")
        return v

    @property
    def nginx_site_available(self) -> Path:
        return self.nginx.site_available(f"{self.site_name}.conf")

    @property
    def nginx_site_enabled(self) -> Path:
        return self.nginx.site_enabled(f"{self.site_name}.conf")

    @property
    def mounts(self) -> Mounts:
        return [
            ("/sub/", str(self.clash.configs_store_dir.resolve())),
            ("/files/", str(FILES_DIR))
             ]
