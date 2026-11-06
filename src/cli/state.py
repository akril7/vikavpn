from dataclasses import dataclass

from src.bootstrap.registry import Registry
from src.configuration import Settings


@dataclass
class CliContext:
    settings: Settings
    registry: Registry

    def reload(self) -> None:
        """Перечитать .env и пересоздать Registry."""
        self.settings = Settings()
        self.registry = Registry(self.settings)
