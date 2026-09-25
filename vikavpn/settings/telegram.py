from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: str
    username: str

    admin_username: str
    guide_video_file_id: str = Field(
        default="BAACAgIAAxkDAAIBPmqyYVEBjWjdUlbxv9SRvJGE-WnNAAJaqAAC4kGQSatz9xeThijiPQQ",
        frozen=True)

    service: str = Field(default="vikavpn-telegram-bot", frozen=True)

    expire_notif_hour: int = Field(default=15, ge=0, le=23)
    expire_notif_minute: int = Field(default=0, ge=0, le=59)
