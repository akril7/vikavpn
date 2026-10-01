import uuid
from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class MTProxyLMode(StrEnum):
    MANAGER = "manager"
    REANIMATOR = "reanimator"


class MTProxyLSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="MTPROXYL_")

    # Порт для подлючения
    port: int = 7443

    # Режим управления telemt
    mode: MTProxyLMode = Field(default=MTProxyLMode.MANAGER)

    # Использовать фикс zapret2
    use_zapret2: bool = True

    # Sni для маскировки
    sni: str = "aeza.ru"

    # Пользователь по умолчанию (для задач управления)
    default_user: str = "default"
    default_user_uuid: str = Field(default_factory=lambda: uuid.uuid4().hex)

    # Путь до secrets.conf файла mtproxyl
    secrets_path: Path = Path("/opt/mtproxyl/secrets.conf")

    # URL для скачивание скрипта установки mtproxyl
    install_script_link: str = (
        "https://raw.githubusercontent.com/Liafanx/MTProxyL/main/install.sh"
    )
