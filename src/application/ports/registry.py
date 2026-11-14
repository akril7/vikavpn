from typing import Protocol

from src.application.ports.services import Configurator, Controller, Installer


class RegistryLike(Protocol):
    @property
    def names_of_installers(self) -> list[str]:
        ...

    @property
    def names_of_controllers(self) -> list[str]:
        ...

    @property
    def names_of_configurators(self) -> list[str]:
        ...

    def get_installer(self, name: str) -> Installer:
        ...

    def get_controller(self, name: str) -> Controller:
        ...

    def get_configurator(self, name: str) -> Configurator:
        ...
