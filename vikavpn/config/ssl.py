from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# noinspection PyNestedDecorators
class TLSSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    domain: str = Field(alias="SERVER_NAME")
    cert_path: Path = Field(alias="CERT_PATH")
    key_path: Path = Field(alias="KEY_PATH")

    @field_validator("cert_path", "key_path")
    @classmethod
    def check_exists(cls, v: Path, info) -> Path:
        if not v.exists():
            raise ValueError(f"{info.field_name} не существует: {v}")
        return v
