from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class YoomoneySettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="YOOMONEY_")

    # Кошелек получателя платежей
    receiver: str

    # Секрет для проверки подписи
    secret: str

    # Процент комиссии за платеж
    fee_percent: float = Field(default=3.0, ge=0)
