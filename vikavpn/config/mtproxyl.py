from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MTProxyLMode(StrEnum):
    MANAGER = "manager"
    REANIMATOR = "reanimator"


class MTProxyLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MTPROXYL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = Field(default=7443, ge=1, le=49151)
    default_user: str = "default"
    default_user_uuid: str = "c97a7565cf5146b63d8e31f8f95da840"
    secrets_path: Path = Path("/opt/mtproxyl/secrets.conf")
    install_script_link: str = (
        "https://raw.githubusercontent.com/Liafanx/MTProxyL/main/install.sh"
    )
    mode: MTProxyLMode = Field(default=MTProxyLMode.MANAGER, frozen=True)
    use_zapret2: bool = True
