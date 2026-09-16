from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import DEFAULT_INSTALL_DIR


class MitaProtocol(StrEnum):
    TCP = "TCP"
    UDP = "UDP"


class MitaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MITA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port_range: str = "10000-10127"
    protocol: MitaProtocol = MitaProtocol.UDP
    service: str = Field(default="mita", frozen=True)
    package_download_link: str = (
        "https://github.com/enfein/mieru/releases/download/v3.36.1/"
        "mita_3.36.1_amd64.deb"
    )

    config_path: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "mita" / "mita.json"
    )
