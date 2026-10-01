from enum import StrEnum

from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class MitaProtocol(StrEnum):
    TCP = "TCP"
    UDP = "UDP"


class MitaSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="MITA_")

    # Диапазон портов для подключения
    port_range: str = "10000-10127"

    # Протокол для сервера
    protocol: MitaProtocol = MitaProtocol.UDP

    # Имя сервиса
    service_name: str = "mita"

    # Устанавливаемая версия бинарника
    version: str = "3.36.1"

    @property
    def package_download_link(self):
        return f"https://github.com/enfein/mieru/releases/download/v{self.version}/mita_{self.version}_amd64.deb"
