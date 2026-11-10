from typing import Protocol

from src.application.ports.services import Configurator, Controller, Installer


class RegistryLike(Protocol):
    def get_names_of_installers(self) -> list[str]:
        ...

    def get_names_of_controllers(self) -> list[str]:
        ...

    def get_names_of_configurator(self) -> list[str]:
        ...

    def get_installer(self, name: str) -> Installer:
        ...

    def get_controller(self, name: str) -> Controller:
        ...

    def get_configurator(self, name: str) -> Configurator:
        ...
