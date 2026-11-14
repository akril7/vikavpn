from pydantic_settings import BaseSettings

from src.configuration.base import make_config


class MicrowarpSettings(BaseSettings):
    model_config = make_config(env_prefix="MICROWARP_")

    image: str = "ghcr.io/ccbkkb/microwarp:latest"
    container_name: str = "microwarp"
    port: int = 1089
