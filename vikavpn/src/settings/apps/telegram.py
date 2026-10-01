from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class TelegramBotSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="TELEGRAM_")

    token: str
    username: str

    admin_username: str

    expire_notif_hour: int = Field(default=15, ge=0, le=23)
    expire_notif_minute: int = Field(default=0, ge=0, le=59)
