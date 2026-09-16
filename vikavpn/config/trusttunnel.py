from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import DEFAULT_INSTALL_DIR


class TrustTunnelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TRUSTTUNNEL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = Field(default=8443, ge=1, le=49151)
    service: str = "trusttunnel"
    install_dir: Path = Field(
        default_factory=lambda: DEFAULT_INSTALL_DIR / "trusttunnel"
    )
    archive_download_link: str = (
        "https://github.com/TrustTunnel/TrustTunnel/releases/download/"
        "v1.1.0/trusttunnel-v1.1.0-linux-x86_64.tar.gz"
    )
