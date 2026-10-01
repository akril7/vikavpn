from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


# noinspection PyNestedDecorators
class TLSSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="")

    # Домен для сервера
    domain: str

    # Путь до файла сертификата для домена
    cert_path: Path

    # Путь до приватного ключа сертификата домена
    key_path: Path

    @field_validator("cert_path", "key_path")
    @classmethod
    def check_exists(cls, v: Path, info) -> Path:
        """ Проверяем, что путь до сертификата существовуют"""

        if not v.exists():
            raise ValueError(f"{info.field_name} не существует: {v}")
        return v
