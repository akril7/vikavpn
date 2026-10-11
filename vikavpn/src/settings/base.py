from pydantic_settings import SettingsConfigDict


def make_config(env_prefix: str = "") -> SettingsConfigDict:
    """Единая конфигурация для всех BaseSettings"""
    if env_prefix and not env_prefix.endswith("_"):
        raise ValueError(f"env_prefix must end with '_': {env_prefix!r}")

    return SettingsConfigDict(
        env_prefix=env_prefix,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )
