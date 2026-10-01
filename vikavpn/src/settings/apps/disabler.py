from pydantic import Field
from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class DisablerSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="DISABLER_")

    hours_delay: int = Field(default=1, ge=0)
