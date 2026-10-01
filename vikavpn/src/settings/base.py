from pydantic_settings import SettingsConfigDict


class BaseSettingsConfigDict(SettingsConfigDict):
    def __init__(self, env_prefix: str):
        super().__init__(
            env_prefix=env_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
            frozen=True
        )
