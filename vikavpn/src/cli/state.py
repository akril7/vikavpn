from dataclasses import dataclass

from src.infrastructure.manager.registry import Registry
from src.settings import Settings


@dataclass
class CliContext:
    settings: Settings
    registry: Registry

    def reload(self) -> None:
        """Перечитать .env и пересоздать Registry."""
        self.settings = Settings()
        self.registry = Registry(self.settings)
