from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class YoomoneySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="YOOMONEY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    receiver: str
    secret: str
    webhook_service: str = Field(default="vikavpn-yoomoney-webhook")
    webhook_path: str = Field(default="/webhook/yoomoney")
    webhook_host: str = Field(default="127.0.0.1")
    webhook_port: int = Field(default=8081)
